package model

import (
	"bytes"
	"context"
	"github.com/jackc/pgx/v5"
)

type IUserbotService interface {
	CreateUserbot(ctx context.Context, accountID int) (*bytes.Buffer, error)
	StartAll(ctx context.Context)
	SendMessage(ctx context.Context, userbotWaPhoneNumber, contactWaPhoneNumber, text string) error
}

type IUserbotRepo interface {
	CreateUserbot(ctx context.Context, accountID int, userbotWaPhoneNumber string) error
}

type IAmocrmSourceService interface {
	CreateAmocrmSource(ctx context.Context, amocrmPipelineID int, userbotWaPhoneNumber string) error
	DeleteAmocrmSource(ctx context.Context, amocrmToken, amocrmSubdomain string, amocrmSourceID int) error
	AmocrmSourceByUserbotWaPhoneNumber(ctx context.Context, userbotWaPhoneNumber string) ([]*AmocrmSource, error)
	NewChat(ctx context.Context,
		amocrmPipelineID int,
		amocrmScopeID,
		contactName,
		contactWaPhoneNumber string,
	) (int, string, string, int, error)
	ImportMessageFromUserbotToAmocrm(ctx context.Context,
		userbotWaPhoneNumber,
		contactWaPhoneNumber,
		text string,
		isGroupChat bool,
	) error

	SendMessageFromAmocrmToContact(ctx context.Context,
		text,
		amocrmExternalID,
		amocrmChatID,
		amocrmMessageID,
		amocrmContactName,
		contactWaPhoneNumber string,
		sendMessage func(ctx context.Context, userbotWaPhoneNumber, contactWaPhoneNumber, text string) error,
	) error

	SendMessageFromContactToAmocrm(ctx context.Context,
		userbotWaPhoneNumber,
		contactWaPhoneNumber,
		text string,
		isGroupChat bool,
	) error
}

type IAmocrmSourceRepo interface {
	CreateAmocrmSource(ctx context.Context,
		amocrmSourceID,
		amocrmPipelineID int,
		userbotWaPhoneNumber,
		amocrmExternalID,
		amocrmScopeID string,
	) error
	AmocrmSourceByUserbotWaPhoneNumber(ctx context.Context, userbotWaPhoneNumber string) ([]*AmocrmSource, error)
	AmocrmSourceByAmocrmExternalID(ctx context.Context, amocrmExternalID string) ([]*AmocrmSource, error)
	CreateContact(ctx context.Context,
		contactWaPhoneNumber string,
		amocrmContactID int,
	) (int, error)
	ContactByWaPhoneNumber(ctx context.Context, contactWaPhoneNumber string) ([]*AmocrmContact, error)
	ContactByID(ctx context.Context, contactID int) ([]*AmocrmContact, error)
	CreateChat(ctx context.Context, contactID int, amocrmConversationID, amocrmChatID string) (int, error)
	ChatByContactID(ctx context.Context, contactID int) ([]*AmocrmChat, error)
	ChatByAmocrmChatID(ctx context.Context, amocrmChatID string) ([]*AmocrmChat, error)
	CreateMessage(ctx context.Context, chatID int, amocrmMessageID, role, text string) error
}

type IAmocrmClient interface {
	CreateSource(ctx context.Context,
		amocrmPipelineID int,
		sourceName,
		amocrmExternalID,
		amocrmToken,
		amocrmSubdomain string,
	) (int, error)

	ConnectChannelToAccount(ctx context.Context,
		amocrmToken,
		amocrmSubdomain string,
	) (string, error)

	CreateContact(ctx context.Context,
		amocrmToken,
		amocrmSubdomain,
		contactPhoneNumber,
		contactName string,
	) (int, error)

	CreateLead(ctx context.Context,
		amocrmToken,
		amocrmSubdomain string,
		amocrmContactID,
		amocrmPipelineID int,
	) (int, error)

	UpdateMessageStatus(ctx context.Context,
		status int,
		amocrmMessageID,
		amocrmScopeID string,
	) error

	CreateChat(ctx context.Context,
		amocrmContactID int,
		amocrmConversationID,
		amocrmScopeID,
		contactName string,
	) (string, error)

	AssignChatToContact(ctx context.Context,
		amocrmToken string,
		amocrmSubdomain string,
		amocrmChatID string,
		amocrmContactID int,
	) error

	SendMessageFromContact(ctx context.Context,
		amocrmContactID int,
		amocrmConversationID,
		amocrmChatID,
		amocrmExternalID,
		amocrmScopeID,
		contactName,
		text string,
	) (string, error)

	ImportMessageFromUserbotToAmocrm(ctx context.Context,
		amocrmContactID int,
		amocrmConversationID,
		amocrmChatID,
		amocrmExternalID,
		amocrmScopeID,
		contactName,
		text string,
	) (string, error)

	ContactIDByNameAndPhone(ctx context.Context,
		amocrmToken,
		amocrmSubdomain,
		amocrmContactName,
		amocrmContactPhone string,
	) (int, error)

	DeleteSource(ctx context.Context,
		amocrmToken,
		amocrmSubdomain string,
		sourceID int,
	) error
}

type IDB interface {
	Insert(ctx context.Context, query string, args ...any) (any, error)
	Select(ctx context.Context, query string, args ...any) (pgx.Rows, error)
	Delete(ctx context.Context, query string, args ...any) error
	Update(ctx context.Context, query string, args ...any) error

	CtxWithTx(ctx context.Context) (context.Context, error)
	CommitTx(ctx context.Context) error
	RollbackTx(ctx context.Context)

	CreateTable(ctx context.Context, query string) error
	DropTable(ctx context.Context, query string) error
}
