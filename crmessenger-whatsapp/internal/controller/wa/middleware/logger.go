package middleware

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"fmt"
	"github.com/google/uuid"
	"go.mau.fi/whatsmeow/types/events"
	"log/slog"
	"runtime/debug"
	"time"
)

func LoggerMiddleware(
	messageHandler func(ctx context.Context, event *events.Message) error,
	joinedGroupHandler func(ctx context.Context, event *events.JoinedGroup) error,
	loggerType,
	serviceName,
	userbotWaPhoneNumber string,
) func(evt interface{}) {
	return func(evt interface{}) {
		defer func() {
			if r := recover(); r != nil {
				fmt.Println(string(debug.Stack()))
			}
		}()
		start := time.Now()
		requestID := uuid.NewString()

		var logger *slog.Logger
		var contactWaPhoneNumber string
		switch event := evt.(type) {
		case *events.Message:
			if event.Info.Sender.User != userbotWaPhoneNumber {
				contactWaPhoneNumber = event.Info.Sender.User
			} else {
				contactWaPhoneNumber = event.Info.RecipientAlt.User
			}
			if loggerType == "dev" {
				logger = slog.With(
					slog.String("contact_wa_phone_number", contactWaPhoneNumber),
					slog.String("userbot_wa_phone_number", userbotWaPhoneNumber),
				)
			} else {
				logger = slog.With(
					slog.String("request_id", requestID),
					slog.String("service_name", serviceName),
					slog.String("contact_wa_phone_number", contactWaPhoneNumber),
					slog.String("userbot_wa_phone_number", userbotWaPhoneNumber),
				)
			}
			ctx := context.WithValue(context.Background(), model.LoggerKey, logger)
			ctx = context.WithValue(ctx, model.RequestIDKey, requestID)
			logger.Info("Request started")

			err := messageHandler(ctx, event)
			duration := float64(time.Since(start)) / 1e6
			if err != nil {
				logger.Error("request failed: "+err.Error(),
					slog.Float64("duration_ms", duration),
				)
			} else {
				logger.Info("request completed",
					slog.Int("http_status", 200),
					slog.Float64("duration_ms", duration),
				)
			}
		case *events.JoinedGroup:
			contactWaPhoneNumber = event.GroupInfo.JID.User

			if loggerType == "dev" {
				logger = slog.With(
					slog.String("contact_wa_phone_number", contactWaPhoneNumber),
					slog.String("userbot_wa_phone_number", userbotWaPhoneNumber),
				)
			} else {
				logger = slog.With(
					slog.String("request_id", requestID),
					slog.String("service_name", serviceName),
					slog.String("contact_wa_phone_number", contactWaPhoneNumber),
					slog.String("userbot_wa_phone_number", userbotWaPhoneNumber),
				)
			}
			ctx := context.WithValue(context.Background(), model.LoggerKey, logger)
			ctx = context.WithValue(ctx, model.RequestIDKey, requestID)
			logger.Info("Request started")

			err := joinedGroupHandler(ctx, event)
			duration := float64(time.Since(start)) / 1e6
			if err != nil {
				logger.Error("request failed: "+err.Error(),
					slog.Float64("duration_ms", duration),
				)
			} else {
				logger.Info("request completed",
					slog.Int("http_status", 200),
					slog.Float64("duration_ms", duration),
				)
			}
		}
	}
}
