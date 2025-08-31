package wa_device_db

import (
	"context"
	_ "github.com/jackc/pgx/v5/stdlib"
	"go.mau.fi/whatsmeow/store/sqlstore"
)

func New(username, password, host, port, dbname string) *sqlstore.Container {
	ctx := context.Background()
	address := "host=" + host + " port=" + port + " user=" + username + " password=" + password + " dbname=" + dbname + " sslmode=disable"
	deviceStore, err := sqlstore.New(ctx, "pgx", address, nil)
	if err != nil {
		panic(err)
	}
	return deviceStore
}
