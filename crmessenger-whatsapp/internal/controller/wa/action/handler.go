package action

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"fmt"
	"go.mau.fi/whatsmeow/types/events"
)

func JoinGroupChatHandler(
	amocrmSourceService model.IAmocrmSourceService,
	userbotWaPhoneNumber string,
) func(ctx context.Context, event *events.JoinedGroup) error {
	return func(ctx context.Context, event *events.JoinedGroup) error {
		amocrmSource, err := amocrmSourceService.AmocrmSourceByUserbotWaPhoneNumber(ctx, userbotWaPhoneNumber)
		if err != nil {
			return err
		}
		fmt.Println(event)

		contactWaPhoneNumber := event.GroupInfo.JID.User
		contactName := event.GroupInfo.Name

		if len(amocrmSource) != 0 {
			_, _, _, _, err = amocrmSourceService.NewChat(ctx,
				amocrmSource[0].AmocrmPipelineID,
				amocrmSource[0].AmocrmScopeID,
				contactName,
				contactWaPhoneNumber,
			)
			if err != nil {
				return err
			}
			err := amocrmSourceService.ImportMessageFromUserbotToAmocrm(ctx,
				userbotWaPhoneNumber,
				contactWaPhoneNumber,
				"Вас добавили в новый групповой чат",
				true,
			)
			if err != nil {
				return err
			}
		}
		return nil
	}
}
