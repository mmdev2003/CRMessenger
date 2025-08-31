package amocrm

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"fmt"
	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/jackc/pgx/v5"
)

func New(db model.IDB) *AmocrmSourceRepo {
	return &AmocrmSourceRepo{db: db}
}

type AmocrmSourceRepo struct {
	db model.IDB
}

func (r *AmocrmSourceRepo) CreateAmocrmSource(ctx context.Context,
	amocrmSourceID,
	amocrmPipelineID int,
	userbotWaPhoneNumber,
	amocrmExternalID,
	amocrmScopeID string,
) error {
	args := pgx.NamedArgs{
		"userbot_wa_phone_number": userbotWaPhoneNumber,
		"amocrm_source_id":        amocrmSourceID,
		"amocrm_pipeline_id":      amocrmPipelineID,
		"amocrm_external_id":      amocrmExternalID,
		"amocrm_scope_id":         amocrmScopeID,
	}
	_, err := r.db.Insert(ctx, CreateAmocrmSource, args)
	if err != nil {
		return err
	}
	return nil
}

func (r *AmocrmSourceRepo) AmocrmSourceByUserbotWaPhoneNumber(ctx context.Context,
	userbotWaPhoneNumber string,
) ([]*model.AmocrmSource, error) {
	args := pgx.NamedArgs{
		"userbot_wa_phone_number": userbotWaPhoneNumber,
	}
	rows, err := r.db.Select(ctx, AmocrmSourceByWaPhoneNumber, args)
	if err != nil {
		return nil, err
	}

	var source []*model.AmocrmSource
	err = pgxscan.ScanAll(&source, rows)
	if err != nil {
		return nil, err
	}

	return source, nil
}

func (r *AmocrmSourceRepo) AmocrmSourceByAmocrmExternalID(ctx context.Context,
	amocrmExternalID string,
) ([]*model.AmocrmSource, error) {
	args := pgx.NamedArgs{
		"amocrm_external_id": amocrmExternalID,
	}
	rows, err := r.db.Select(ctx, AmocrmSourceByExternalID, args)
	if err != nil {
		return nil, err
	}

	var source []*model.AmocrmSource
	err = pgxscan.ScanAll(&source, rows)
	if err != nil {
		return nil, err
	}

	return source, nil
}

func (r *AmocrmSourceRepo) CreateContact(ctx context.Context,
	contactWaPhoneNumber string,
	amocrmContactID int,
) (int, error) {
	args := pgx.NamedArgs{
		"wa_phone_number":   contactWaPhoneNumber,
		"amocrm_contact_id": amocrmContactID,
	}
	contactID, err := r.db.Insert(ctx, CreateContact, args)
	if err != nil {
		return 0, err
	}

	switch contactID := contactID.(type) {
	case int:
		return contactID, nil
	case int64:
		return int(contactID), nil
	case int32:
		return int(contactID), nil
	}
	return 0, fmt.Errorf("type %T is not supported", contactID)
}

func (r *AmocrmSourceRepo) ContactByWaPhoneNumber(ctx context.Context,
	contactWaPhoneNumber string,
) ([]*model.AmocrmContact, error) {
	args := pgx.NamedArgs{
		"wa_phone_number": contactWaPhoneNumber,
	}
	rows, err := r.db.Select(ctx, ContactByWaPhoneNumber, args)
	if err != nil {
		return nil, err
	}

	var contact []*model.AmocrmContact
	err = pgxscan.ScanAll(&contact, rows)
	if err != nil {
		return nil, err
	}

	return contact, nil
}

func (r *AmocrmSourceRepo) ContactByID(ctx context.Context,
	contactID int,
) ([]*model.AmocrmContact, error) {
	args := pgx.NamedArgs{
		"contact_id": contactID,
	}
	rows, err := r.db.Select(ctx, ContactByID, args)
	if err != nil {
		return nil, err
	}

	var contact []*model.AmocrmContact
	err = pgxscan.ScanAll(&contact, rows)
	if err != nil {
		return nil, err
	}

	return contact, nil
}

func (r *AmocrmSourceRepo) CreateChat(ctx context.Context,
	contactID int,
	amocrmConversationID,
	amocrmChatID string,
) (int, error) {
	args := pgx.NamedArgs{
		"contact_id":             contactID,
		"amocrm_conversation_id": amocrmConversationID,
		"amocrm_chat_id":         amocrmChatID,
	}
	fmt.Println(args)
	chatID, err := r.db.Insert(ctx, CreateChat, args)
	if err != nil {
		return 0, err
	}
	switch chatID := chatID.(type) {
	case int:
		return chatID, nil
	case int64:
		return int(chatID), nil
	case int32:
		return int(chatID), nil
	}
	return 0, fmt.Errorf("type %T is not supported", contactID)
}

func (r *AmocrmSourceRepo) ChatByContactID(ctx context.Context,
	contactID int,
) ([]*model.AmocrmChat, error) {
	args := pgx.NamedArgs{
		"contact_id": contactID,
	}
	rows, err := r.db.Select(ctx, ChatByContactID, args)
	if err != nil {
		return nil, err
	}

	var chat []*model.AmocrmChat
	err = pgxscan.ScanAll(&chat, rows)
	if err != nil {
		return nil, err
	}

	return chat, nil
}

func (r *AmocrmSourceRepo) ChatByAmocrmChatID(ctx context.Context,
	amocrmChatID string,
) ([]*model.AmocrmChat, error) {
	args := pgx.NamedArgs{
		"amocrm_chat_id": amocrmChatID,
	}
	rows, err := r.db.Select(ctx, ChatByAmocrmChatID, args)
	if err != nil {
		return nil, err
	}

	var chat []*model.AmocrmChat
	err = pgxscan.ScanAll(&chat, rows)
	if err != nil {
		return nil, err
	}

	return chat, nil
}

func (r *AmocrmSourceRepo) CreateMessage(ctx context.Context,
	chatID int,
	amocrmMessageID,
	role,
	text string,
) error {
	args := pgx.NamedArgs{
		"chat_id":           chatID,
		"amocrm_message_id": amocrmMessageID,
		"role":              role,
		"text":              text,
	}
	_, err := r.db.Insert(ctx, CreateMessage, args)
	if err != nil {
		return err
	}
	return nil
}
