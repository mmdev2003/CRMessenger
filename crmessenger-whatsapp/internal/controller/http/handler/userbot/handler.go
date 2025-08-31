package userbot

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"net/http"
)
import "github.com/labstack/echo/v4"

func CreateUserbot(userbotService model.IUserbotService) func(ctx echo.Context) error {
	return func(request echo.Context) error {
		ctx := request.Request().Context()
		ctx = context.WithValue(ctx, model.LoggerKey, request.Get("logger"))
		ctx = context.WithValue(ctx, model.RequestIDKey, request.Get("requestID"))

		var body CreateUserbotBody
		if err := request.Bind(&body); err != nil {
			return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
		}
		if err := request.Validate(&body); err != nil {
			return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
		}

		qrCode, err := userbotService.CreateUserbot(ctx, body.AccountID)
		if err != nil {
			return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
		}
		return request.Blob(http.StatusOK, "image/png", qrCode.Bytes())
	}
}
