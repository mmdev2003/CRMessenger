from opentelemetry import trace, metrics, propagate
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ALWAYS_ON
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagators.composite import CompositePropagator

from internal import interface
from .logger import OtelLogger

class Telemetry(interface.ITelemetry):
    def __init__(
            self,
            log_level: str,
            root_path: str,
            environment: str,
            service_name: str,
            service_version: str,
            otlp_host: str,
            otlp_port: int,
    ):

        self.log_level = log_level
        self.environment = environment
        self.root_path = root_path
        self.service_name = service_name
        self.service_version = service_version
        self.otlp_endpoint = f"{otlp_host}:{otlp_port}"

        self._setup_telemetry()

    def _setup_telemetry(self) -> None:
        resource = self._create_resource()
        self._setup_tracing(resource)
        self._setup_metrics(resource)
        self._setup_logging(resource)
        self._setup_propagators()
        self._setup_logger()

        self._logger.info("Telemetry initialized successfully")

    def _create_resource(self) -> Resource:
        return Resource.create({
            ResourceAttributes.SERVICE_NAME: self.service_name,
            ResourceAttributes.SERVICE_VERSION: self.service_version,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.environment,
        })

    def _setup_tracing(self, resource: Resource) -> None:
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"http://{self.otlp_endpoint}",
            insecure=True
        )

        if self.environment == "prod":
            sampler = TraceIdRatioBased(0.6)
        else:
            sampler = ALWAYS_ON

        self._tracer_provider = TracerProvider(
            resource=resource,
            sampler=sampler
        )

        span_processor = BatchSpanProcessor(
            otlp_exporter,
            max_export_batch_size=512,
            max_queue_size=2048,
            export_timeout_millis=5000
        )
        self._tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(self._tracer_provider)

        self._tracer = self._tracer_provider.get_tracer(
            self.service_name,
            self.service_version
        )

    def _setup_metrics(self, resource: Resource) -> None:
        otlp_exporter = OTLPMetricExporter(
            endpoint=f"http://{self.otlp_endpoint}",
            insecure=True
        )

        reader = PeriodicExportingMetricReader(
            exporter=otlp_exporter,
            export_interval_millis=30000
        )

        self._meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[reader]
        )

        metrics.set_meter_provider(self._meter_provider)

        self._meter = self._meter_provider.get_meter(
            self.service_name,
            self.service_version
        )

    def _setup_logging(self, resource: Resource) -> None:
        otlp_exporter = OTLPLogExporter(
            endpoint=f"http://{self.otlp_endpoint}",
            insecure=True
        )

        processor = BatchLogRecordProcessor(
            otlp_exporter,
            max_export_batch_size=512,
            export_timeout_millis=5000
        )

        self._logger_provider = LoggerProvider(resource=resource)
        self._logger_provider.add_log_record_processor(processor)

        set_logger_provider(self._logger_provider)

    @staticmethod
    def _setup_propagators() -> None:
        propagate.set_global_textmap(
            CompositePropagator([
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator(),
            ])
        )

    def _setup_logger(self) -> None:
        self._logger = OtelLogger(
            self._logger_provider,
            self.service_name
        )

    def logger(self) -> interface.IOtelLogger:
        return self._logger

    def tracer(self) -> trace.Tracer:
        return self._tracer

    def meter(self) -> metrics.Meter:
        return self._meter

    def shutdown(self) -> None:
        errors = []

        try:
            if hasattr(self, '_tracer_provider'):
                self._tracer_provider.shutdown()
        except Exception as e:
            errors.append(f"tracer provider shutdown: {e}")

        try:
            if hasattr(self, '_meter_provider'):
                self._meter_provider.shutdown()
        except Exception as e:
            errors.append(f"meter provider shutdown: {e}")

        try:
            if hasattr(self, '_logger_provider'):
                self._logger_provider.shutdown()
        except Exception as e:
            errors.append(f"logger provider shutdown: {e}")

        if errors:
            raise Exception(f"shutdown errors: {errors}")
