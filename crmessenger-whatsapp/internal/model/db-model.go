package model

import "time"

type AmocrmSource struct {
	AmocrmSourceID       int       `db:"amocrm_source_id"`
	UserbotWaPhoneNumber string    `db:"userbot_wa_phone_number"`
	AmocrmPipelineID     int       `db:"amocrm_pipeline_id"`
	AmocrmExternalID     string    `db:"amocrm_external_id"`
	AmocrmScopeID        string    `db:"amocrm_scope_id"`
	CreatedAt            time.Time `db:"created_at"`
	UpdatedAt            time.Time `db:"updated_at"`
}

type Userbot struct {
	WaPhoneNumber string `db:"wa_phone_number"`

	AccountID int `db:"account_id"`

	CreatedAt time.Time `db:"created_at"`
	UpdatedAt time.Time `db:"updated_at"`
}

type AmocrmContact struct {
	ID              int       `db:"id"`
	WaPhoneNumber   string    `db:"wa_phone_number"`
	AmocrmContactID int       `db:"amocrm_contact_id"`
	CreatedAt       time.Time `db:"created_at"`
	UpdatedAt       time.Time `db:"updated_at"`
}

type AmocrmChat struct {
	ID                   int       `db:"id"`
	ContactID            int       `db:"contact_id"`
	AmocrmConversationID string    `db:"amocrm_conversation_id"`
	AmocrmChatID         string    `db:"amocrm_chat_id"`
	CreatedAt            time.Time `db:"created_at"`
	UpdatedAt            time.Time `db:"updated_at"`
}

type AmocrmMessage struct {
	ID          int    `db:"id"`
	ChatID      int    `db:"chat_id"`
	Text        string `db:"text"`
	AmocrmMsgID string `db:"amocrm_message_id"`
}
