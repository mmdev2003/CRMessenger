package amocrm

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"fmt"
	"github.com/labstack/echo/v4"
	"net/http"
)

func CreateAmocrmSource(
	amocrmSourceService model.IAmocrmSourceService,
) func(ctx echo.Context) error {
	return func(request echo.Context) error {
		ctx := request.Request().Context()
		ctx = context.WithValue(ctx, model.LoggerKey, request.Get("logger"))
		ctx = context.WithValue(ctx, model.RequestIDKey, request.Get("requestID"))

		var body CreateAmocrmSourceBody
		if err := request.Bind(&body); err != nil {
			return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
		}
		if err := request.Validate(&body); err != nil {
			return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
		}

		err := amocrmSourceService.CreateAmocrmSource(ctx,
			body.AmocrmPipelineID,
			body.UserbotWaPhoneNumber,
		)
		if err != nil {
			return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
		}
		return request.JSON(http.StatusOK, "ok")
	}
}

func SendMessageFromAmocrm(
	amocrmSourceService model.IAmocrmSourceService,
	userbotService model.IUserbotService,
) func(request echo.Context) error {
	return func(request echo.Context) error {
		ctx := request.Request().Context()
		ctx = context.WithValue(ctx, model.LoggerKey, request.Get("logger"))
		ctx = context.WithValue(ctx, model.RequestIDKey, request.Get("requestID"))

		var body TextMessageFromAmocrmBody
		if err := request.Bind(&body); err != nil {
			return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
		}
		if err := request.Validate(&body); err != nil {
			return echo.NewHTTPError(http.StatusUnprocessableEntity, err.Error())
		}

		fmt.Println(body)
		text := body.Message.Message.Text
		amocrmMessageID := body.Message.Message.ID
		amocrmChatID := body.Message.Conversation.ID
		amocrmExternalID := body.Message.Source["external_id"].(string)
		amocrmContactName := body.Message.Receiver["name"].(string)
		amocrmContactPhone, ok := body.Message.Receiver["phone"].(string)
		if !ok {
			amocrmContactPhone = "Он нужен, только если менеджер пишет первым из интерфейса амо"
		}

		err := amocrmSourceService.SendMessageFromAmocrmToContact(ctx,
			text,
			amocrmExternalID,
			amocrmChatID,
			amocrmMessageID,
			amocrmContactName,
			amocrmContactPhone,
			userbotService.SendMessage,
		)
		if err != nil {
			return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
		}

		return nil
	}
}
