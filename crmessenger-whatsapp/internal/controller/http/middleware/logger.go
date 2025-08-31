package middleware

import (
	"crmessenger-whatsapp/internal/model"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"log/slog"
	"strings"
	"time"
)

func LoggerMiddleware(
	loggerType,
	prefix,
	serviceName string,
) func(next echo.HandlerFunc) echo.HandlerFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(request echo.Context) error {
			if !strings.Contains(request.Request().URL.Path, prefix) {
				return request.JSON(404, echo.Map{"error": "not found"})
			}

			start := time.Now()
			requestID := request.Request().Header.Get("X-Request-ID")
			if requestID == "" {
				requestID = uuid.NewString()
				request.Request().Header.Set("X-Request-ID", requestID)
			}

			var logger *slog.Logger
			if loggerType == "dev" {
				logger = slog.With(
					slog.String("http_method", request.Request().Method),
					slog.String("http_path", request.Request().URL.Path),
				)
			} else {
				logger = slog.With(
					slog.Any("request_id", requestID),
					slog.Any("http_method", request.Request().Method),
					slog.Any("http_path", request.Request().URL.Path),
					slog.Any("service_name", serviceName),
				)
			}

			request.Set(model.LoggerKey, logger)
			request.Set(model.RequestIDKey, requestID)

			logger.Info("Request started")
			err := next(request)
			duration := float64(time.Since(start)) / 1e6
			if err != nil {
				logger.Error("request failed: "+err.Error(),
					slog.Float64("duration_ms", duration),
				)
			} else {
				logger.Info("request completed",
					slog.Int("http_status", request.Response().Status),
					slog.Float64("duration_ms", duration),
				)
			}
			return err
		}
	}
}
