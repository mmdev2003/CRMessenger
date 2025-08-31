package message

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"fmt"
	"go.mau.fi/whatsmeow/types/events"
)

func EventMessageHandler(
	amocrmSourceService model.IAmocrmSourceService,
	userbotWaPhoneNumber string,
) func(ctx context.Context, event *events.Message) error {
	return func(ctx context.Context, event *events.Message) error {
		//amocrmSource, err := amocrmSourceService.AmocrmSourceByUserbotWaPhoneNumber(ctx, userbotWaPhoneNumber)
		//if err != nil {
		//	return err
		//}
		//
		//var isGroup bool
		//if event.Info.IsGroup {
		//	isGroup = true
		//} else {
		//	isGroup = false
		//}
		fmt.Println(event)
		//if event.Info.Sender.User != userbotWaPhoneNumber {
		//	contactWaPhoneNumber := event.Info.Sender.User
		//
		//	if len(amocrmSource) != 0 {
		//		err = amocrmSourceService.SendMessageFromContactToAmocrm(ctx,
		//			userbotWaPhoneNumber,
		//			contactWaPhoneNumber,
		//			event.Message.GetConversation(),
		//			isGroup,
		//		)
		//		if err != nil {
		//			return err
		//		}
		//	}
		//
		//} else {
		//	contactWaPhoneNumber := event.Info.Chat.User
		//	if len(amocrmSource) != 0 {
		//		err = amocrmSourceService.ImportMessageFromUserbotToAmocrm(ctx,
		//			userbotWaPhoneNumber,
		//			contactWaPhoneNumber,
		//			event.Message.GetConversation(),
		//			isGroup,
		//		)
		//		if err != nil {
		//			return err
		//		}
		//	}
		//}
		return nil
	}
}
