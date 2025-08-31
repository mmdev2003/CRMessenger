package amocrm

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"fmt"
	"github.com/google/uuid"
	"log/slog"
)

func New(
	amocrmRepo model.IAmocrmSourceRepo,
	amocrmClient model.IAmocrmClient,
) *AmocrmSourceService {
	return &AmocrmSourceService{
		amocrmSourceRepo: amocrmRepo,
		amocrmClient:     amocrmClient,
	}
}

type AmocrmSourceService struct {
	amocrmSourceRepo model.IAmocrmSourceRepo
	amocrmClient     model.IAmocrmClient
}

func (s *AmocrmSourceService) CreateAmocrmSource(ctx context.Context,
	amocrmPipelineID int,
	userbotWaPhoneNumber string,
) error {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	amocrmExternalID := uuid.New().String()
	const amocrmToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU5NmVjMzgxYTc1ZDg2OTQ4Nzc2Y2E5MmVmODI4OGFmYzY0Mzg4YmMyMGJiNzk2Yjk2ZjNkOTJiMmNiMWVlNjhhZGFhYTlmYTU3NTExODQ5In0.eyJhdWQiOiI1MTllMjY2NC00Yjk1LTQxYjItYjE3YS1mZWQ1ZDJiNjFiNDIiLCJqdGkiOiJlOTZlYzM4MWE3NWQ4Njk0ODc3NmNhOTJlZjgyODhhZmM2NDM4OGJjMjBiYjc5NmI5NmYzZDkyYjJjYjFlZTY4YWRhYWE5ZmE1NzUxMTg0OSIsImlhdCI6MTc0ODAyMTAzMiwibmJmIjoxNzQ4MDIxMDMyLCJleHAiOjE3NDg2NDk2MDAsInN1YiI6IjEyNTEwODQ2IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMyNDI3ODI2LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYmY5OGQ0NDItNTlhYS00NGE3LTk2YzgtMWVlNDljM2NkNzg4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.WQnYlO58lsNDfT98kB9vsU3anMaP7jySsz4mA4t6HXtPkxILJWPRWsZb144Y_mQSPQLFGlSUV6VTmHquXhf9RFLc4jP1paSbvZO-ibwDbA3wYrovQASLQeu5Juu_0WrdUYDcX4pnKnp2cGY7H2xqvhxBRVxRqEnXTVUv3tvFHPocDQWtzCtIAUGkHOb4cxwte3HsW1f1cUAJ9sKWphWmoMiw7lyxLGAHeacooZSQmzOgrArQyVMU7CYCM96o8hreVh2XpW8KgASTszlWgytakfh-I3IVMUDGKmDwM3E51Mcw3fz1r7WTUg-A5-iNBjZU36fP3PNMeAhXK5kMKNdY9Q"
	const amocrmSubdomain = "mmdev2003yandexru"
	var userbotName = "+" + userbotWaPhoneNumber

	amocrmSourceID, err := s.amocrmClient.CreateSource(ctx,
		amocrmPipelineID,
		userbotName,
		amocrmExternalID,
		amocrmToken,
		amocrmSubdomain,
	)
	if err != nil {
		return err
	}
	logger.Debug("Создали источник в АМОCRM")

	amocrmScopeID, err := s.amocrmClient.ConnectChannelToAccount(ctx,
		amocrmToken,
		amocrmSubdomain,
	)
	if err != nil {
		return err
	}
	logger.Debug("Подключили источник в аккаунт в АМОCRM")

	err = s.amocrmSourceRepo.CreateAmocrmSource(ctx,
		amocrmSourceID,
		amocrmPipelineID,
		userbotWaPhoneNumber,
		amocrmExternalID,
		amocrmScopeID,
	)
	if err != nil {
		return err
	}
	logger.Debug("Создали источник в БД")

	return nil
}

func (s *AmocrmSourceService) AmocrmSourceByUserbotWaPhoneNumber(ctx context.Context,
	userbotWaPhoneNumber string,
) ([]*model.AmocrmSource, error) {
	return s.amocrmSourceRepo.AmocrmSourceByUserbotWaPhoneNumber(ctx, userbotWaPhoneNumber)
}

func (s *AmocrmSourceService) DeleteAmocrmSource(ctx context.Context,
	amocrmToken,
	amocrmSubdomain string,
	amocrmSourceID int,
) error {
	return s.amocrmClient.DeleteSource(ctx, amocrmToken, amocrmSubdomain, amocrmSourceID)
}

func (s *AmocrmSourceService) NewChat(ctx context.Context,
	amocrmPipelineID int,
	amocrmScopeID,
	contactName,
	contactWaPhoneNumber string,
) (int, string, string, int, error) {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	const amocrmToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU5NmVjMzgxYTc1ZDg2OTQ4Nzc2Y2E5MmVmODI4OGFmYzY0Mzg4YmMyMGJiNzk2Yjk2ZjNkOTJiMmNiMWVlNjhhZGFhYTlmYTU3NTExODQ5In0.eyJhdWQiOiI1MTllMjY2NC00Yjk1LTQxYjItYjE3YS1mZWQ1ZDJiNjFiNDIiLCJqdGkiOiJlOTZlYzM4MWE3NWQ4Njk0ODc3NmNhOTJlZjgyODhhZmM2NDM4OGJjMjBiYjc5NmI5NmYzZDkyYjJjYjFlZTY4YWRhYWE5ZmE1NzUxMTg0OSIsImlhdCI6MTc0ODAyMTAzMiwibmJmIjoxNzQ4MDIxMDMyLCJleHAiOjE3NDg2NDk2MDAsInN1YiI6IjEyNTEwODQ2IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMyNDI3ODI2LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYmY5OGQ0NDItNTlhYS00NGE3LTk2YzgtMWVlNDljM2NkNzg4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.WQnYlO58lsNDfT98kB9vsU3anMaP7jySsz4mA4t6HXtPkxILJWPRWsZb144Y_mQSPQLFGlSUV6VTmHquXhf9RFLc4jP1paSbvZO-ibwDbA3wYrovQASLQeu5Juu_0WrdUYDcX4pnKnp2cGY7H2xqvhxBRVxRqEnXTVUv3tvFHPocDQWtzCtIAUGkHOb4cxwte3HsW1f1cUAJ9sKWphWmoMiw7lyxLGAHeacooZSQmzOgrArQyVMU7CYCM96o8hreVh2XpW8KgASTszlWgytakfh-I3IVMUDGKmDwM3E51Mcw3fz1r7WTUg-A5-iNBjZU36fP3PNMeAhXK5kMKNdY9Q"
	const amocrmSubdomain = "mmdev2003yandexru"

	amocrmConversationID := uuid.New().String()

	amocrmContactID, amocrmChatID, err := s.createAmocrmEntities(ctx,
		amocrmToken,
		amocrmSubdomain,
		amocrmScopeID,
		amocrmConversationID,
		amocrmPipelineID,
		contactName,
		contactWaPhoneNumber,
	)
	if err != nil {
		return 0, "", "", 0, err
	}
	logger.Debug("Создали сущности в АМОCRM")

	contactID, err := s.amocrmSourceRepo.CreateContact(ctx,
		contactWaPhoneNumber,
		amocrmContactID,
	)
	if err != nil {
		return 0, "", "", 0, err
	}
	logger.Debug("Создали контакт в БД")

	chatID, err := s.amocrmSourceRepo.CreateChat(ctx,
		contactID,
		amocrmConversationID,
		amocrmChatID,
	)
	if err != nil {
		return 0, "", "", 0, err
	}
	logger.Debug("Создали чат в БД")

	return amocrmContactID, amocrmConversationID, amocrmChatID, chatID, nil
}

func (s *AmocrmSourceService) ImportMessageFromUserbotToAmocrm(ctx context.Context,
	userbotWaPhoneNumber,
	contactWaPhoneNumber,
	text string,
	isGroupChat bool,
) error {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	amocrmSources, err := s.amocrmSourceRepo.AmocrmSourceByUserbotWaPhoneNumber(ctx, userbotWaPhoneNumber)
	if err != nil || len(amocrmSources) == 0 {
		return fmt.Errorf("could not find amocrm source for userbot phone %s", userbotWaPhoneNumber)
	}
	amocrmSource := amocrmSources[0]

	contact, err := s.amocrmSourceRepo.ContactByWaPhoneNumber(ctx, contactWaPhoneNumber)
	if err != nil {
		return err
	}

	contactName := contactWaPhoneNumber
	var amocrmConversationID string
	var amocrmChatID string
	var amocrmContactID int
	var chatID int
	if !isGroupChat && len(contact) == 0 {
		amocrmContactID, amocrmConversationID, amocrmChatID, chatID, err = s.NewChat(ctx,
			amocrmSource.AmocrmPipelineID,
			amocrmSource.AmocrmScopeID,
			contactName,
			contactWaPhoneNumber,
		)
		if err != nil {
			return err
		}

		logger.Debug("Создали сущности в АМОCRM и БД")
	} else {
		chat, err := s.amocrmSourceRepo.ChatByContactID(ctx, contact[0].ID)
		if err != nil {
			return err
		}

		if len(chat) == 0 {
			return fmt.Errorf("could not find chat for contact %d", contact[0].ID)
		}
		amocrmConversationID = chat[0].AmocrmConversationID

		amocrmChatID = chat[0].AmocrmChatID
		amocrmContactID = contact[0].AmocrmContactID
		chatID = chat[0].ID
	}
	if isGroupChat {
		text = fmt.Sprintf("Отправка сообщения от %s:\n\n %s", contactName, text)
	}

	amocrmMessageID, err := s.amocrmClient.ImportMessageFromUserbotToAmocrm(ctx,
		amocrmContactID,
		amocrmConversationID,
		amocrmChatID,
		amocrmSource.AmocrmExternalID,
		amocrmSource.AmocrmScopeID,
		contactName,
		text,
	)
	if err != nil {
		return err
	}
	logger.Debug("Сообщение создано в АМОCRM")

	err = s.amocrmSourceRepo.CreateMessage(ctx,
		chatID,
		amocrmMessageID,
		"manager",
		text,
	)
	if err != nil {
		return err
	}
	logger.Debug("Сообщение создано в БД")
	return nil
}

func (s *AmocrmSourceService) SendMessageFromContactToAmocrm(ctx context.Context,
	userbotWaPhoneNumber,
	contactWaPhoneNumber,
	text string,
	isGroupChat bool,
) error {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	amocrmSources, err := s.amocrmSourceRepo.AmocrmSourceByUserbotWaPhoneNumber(ctx, userbotWaPhoneNumber)
	if err != nil || len(amocrmSources) == 0 {
		return fmt.Errorf("could not find amocrm source for userbot phone %s", userbotWaPhoneNumber)
	}
	amocrmSource := amocrmSources[0]

	contact, err := s.amocrmSourceRepo.ContactByWaPhoneNumber(ctx, contactWaPhoneNumber)
	if err != nil {
		return err
	}

	contactName := contactWaPhoneNumber

	var amocrmConversationID string
	var amocrmChatID string
	var amocrmContactID int
	var chatID int
	if !isGroupChat && len(contact) == 0 {
		amocrmContactID, amocrmConversationID, amocrmChatID, chatID, err = s.NewChat(ctx,
			amocrmSource.AmocrmPipelineID,
			amocrmSource.AmocrmScopeID,
			contactName,
			contactWaPhoneNumber,
		)
		if err != nil {
			return err
		}
		logger.Debug("Создали сущности в АМОCRM и БД")
	} else {
		chat, err := s.amocrmSourceRepo.ChatByContactID(ctx, contact[0].ID)
		if err != nil {
			return err
		}
		amocrmConversationID = chat[0].AmocrmConversationID
		amocrmChatID = chat[0].AmocrmChatID
		amocrmContactID = contact[0].AmocrmContactID
		chatID = chat[0].ID
	}

	if isGroupChat {
		text = fmt.Sprintf("Отправка сообщения от %s:\n\n %s", contactName, text)
	}

	amocrmMessageID, err := s.amocrmClient.SendMessageFromContact(ctx,
		amocrmContactID,
		amocrmConversationID,
		amocrmChatID,
		amocrmSource.AmocrmExternalID,
		amocrmSource.AmocrmScopeID,
		contactName,
		text,
	)
	if err != nil {
		return err
	}
	logger.Debug("Сообщение создано в АМОCRM")

	err = s.amocrmSourceRepo.CreateMessage(ctx,
		chatID,
		amocrmMessageID,
		"contact",
		text,
	)
	if err != nil {
		return err
	}
	logger.Debug("Сообщение создано в БД")
	return nil
}

func (s *AmocrmSourceService) SendMessageFromAmocrmToContact(ctx context.Context,
	text,
	amocrmExternalID,
	amocrmChatID,
	amocrmMessageID,
	amocrmContactName,
	contactWaPhoneNumber string,
	sendMessage func(ctx context.Context, userbotWaPhoneNumber, contactWaPhoneNumber, text string) error,
) error {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	amocrmSource, err := s.amocrmSourceRepo.AmocrmSourceByAmocrmExternalID(ctx, amocrmExternalID)
	if err != nil {
		return err
	}

	chat, err := s.amocrmSourceRepo.ChatByAmocrmChatID(ctx, amocrmChatID)
	if err != nil {
		return err
	}

	if len(chat) == 0 {
		const amocrmToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU5NmVjMzgxYTc1ZDg2OTQ4Nzc2Y2E5MmVmODI4OGFmYzY0Mzg4YmMyMGJiNzk2Yjk2ZjNkOTJiMmNiMWVlNjhhZGFhYTlmYTU3NTExODQ5In0.eyJhdWQiOiI1MTllMjY2NC00Yjk1LTQxYjItYjE3YS1mZWQ1ZDJiNjFiNDIiLCJqdGkiOiJlOTZlYzM4MWE3NWQ4Njk0ODc3NmNhOTJlZjgyODhhZmM2NDM4OGJjMjBiYjc5NmI5NmYzZDkyYjJjYjFlZTY4YWRhYWE5ZmE1NzUxMTg0OSIsImlhdCI6MTc0ODAyMTAzMiwibmJmIjoxNzQ4MDIxMDMyLCJleHAiOjE3NDg2NDk2MDAsInN1YiI6IjEyNTEwODQ2IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMyNDI3ODI2LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYmY5OGQ0NDItNTlhYS00NGE3LTk2YzgtMWVlNDljM2NkNzg4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.WQnYlO58lsNDfT98kB9vsU3anMaP7jySsz4mA4t6HXtPkxILJWPRWsZb144Y_mQSPQLFGlSUV6VTmHquXhf9RFLc4jP1paSbvZO-ibwDbA3wYrovQASLQeu5Juu_0WrdUYDcX4pnKnp2cGY7H2xqvhxBRVxRqEnXTVUv3tvFHPocDQWtzCtIAUGkHOb4cxwte3HsW1f1cUAJ9sKWphWmoMiw7lyxLGAHeacooZSQmzOgrArQyVMU7CYCM96o8hreVh2XpW8KgASTszlWgytakfh-I3IVMUDGKmDwM3E51Mcw3fz1r7WTUg-A5-iNBjZU36fP3PNMeAhXK5kMKNdY9Q"
		const amocrmSubdomain = "mmdev2003yandexru"
		amocrmContactID, err := s.amocrmClient.ContactIDByNameAndPhone(ctx,
			amocrmToken,
			amocrmSubdomain,
			amocrmContactName,
			contactWaPhoneNumber,
		)
		if err != nil {
			return err
		}

		contactID, err := s.amocrmSourceRepo.CreateContact(ctx,
			contactWaPhoneNumber,
			amocrmContactID,
		)
		if err != nil {
			return err
		}
		logger.Debug("Создали контакт в БД")

		amocrmConversationID := uuid.NewString()
		_, err = s.amocrmSourceRepo.CreateChat(ctx,
			contactID,
			amocrmConversationID,
			amocrmChatID,
		)
		if err != nil {
			return err
		}

		chat, err = s.amocrmSourceRepo.ChatByAmocrmChatID(ctx, amocrmChatID)
		if err != nil {
			return err
		}
	}

	contact, err := s.amocrmSourceRepo.ContactByID(ctx, chat[0].ContactID)
	if err != nil {
		return err
	}

	err = sendMessage(ctx,
		amocrmSource[0].UserbotWaPhoneNumber,
		contact[0].WaPhoneNumber,
		text,
	)
	if err != nil {
		return err
	}
	err = s.amocrmSourceRepo.CreateMessage(ctx,
		chat[0].ID,
		amocrmMessageID,
		"manager",
		text,
	)
	if err != nil {
		return err
	}

	return nil
}

func (s *AmocrmSourceService) createAmocrmEntities(ctx context.Context,
	amocrmToken,
	amocrmSubdomain,
	amocrmScopeID,
	amocrmConversationID string,
	amocrmPipelineID int,
	contactName,
	contactWaPhoneNumber string,
) (int, string, error) {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	amocrmContactID, err := s.amocrmClient.CreateContact(ctx, amocrmToken, amocrmSubdomain, contactWaPhoneNumber, contactName)
	if err != nil {
		return 0, "", err
	}
	logger.Debug("Создали контакт в amoCRM")

	amocrmChatID, err := s.amocrmClient.CreateChat(ctx, amocrmContactID, amocrmConversationID, amocrmScopeID, contactName)
	if err != nil {
		return 0, "", err
	}
	logger.Debug("Создали чат в amoCRM")

	err = s.amocrmClient.AssignChatToContact(ctx, amocrmToken, amocrmSubdomain, amocrmChatID, amocrmContactID)
	if err != nil {
		return 0, "", err
	}
	logger.Debug("Привязали чат к контакту в амоСРМ")

	_, err = s.amocrmClient.CreateLead(ctx, amocrmToken, amocrmSubdomain, amocrmContactID, amocrmPipelineID)
	if err != nil {
		return 0, "", err
	}
	logger.Debug("Создали сделку в amoCRM")

	return amocrmContactID, amocrmChatID, nil
}
