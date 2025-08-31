package userbot

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"github.com/jackc/pgx/v5"
)

func New(db model.IDB) *UserbotRepo {
	return &UserbotRepo{db: db}
}

type UserbotRepo struct {
	db model.IDB
}

func (r *UserbotRepo) CreateUserbot(ctx context.Context,
	accountID int,
	waPhoneNumber string,
) error {
	args := pgx.NamedArgs{
		"account_id":      accountID,
		"wa_phone_number": waPhoneNumber,
	}
	_, err := r.db.Insert(ctx, CreateUserbot, args)
	if err != nil {
		return err
	}
	return nil
}
