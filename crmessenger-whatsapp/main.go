package main

import (
	"context"
	"os"
)

import (
	"crmessenger-whatsapp/internal/app/server"
	"crmessenger-whatsapp/internal/config"
	"crmessenger-whatsapp/pkg/logger"
)

import (
	PG "crmessenger-whatsapp/infrastructure/pg"
	WaDeviceDB "crmessenger-whatsapp/infrastructure/wa-device-db"
)

import (
	AmocrmClient "crmessenger-whatsapp/pkg/client/external/amocrm"
)

import (
	AmocrmSourceRepo "crmessenger-whatsapp/internal/repo/amocrm"
	UserbotRepo "crmessenger-whatsapp/internal/repo/userbot"
	AmocrmSourceService "crmessenger-whatsapp/internal/service/amocrm"
	UserbotService "crmessenger-whatsapp/internal/service/userbot"
)

func main() {
	cfg := config.New()
	rootPath, _ := os.Getwd()
	logger.Setup(
		cfg.Logger.Type,
		rootPath,
	)
	db := PG.New(
		cfg.DB.Username,
		cfg.DB.Password,
		cfg.DB.Host,
		cfg.DB.Port,
		cfg.DB.Dbname,
	)
	waDeviceDB := WaDeviceDB.New(
		cfg.WaDeviceDB.Username,
		cfg.WaDeviceDB.Password,
		cfg.WaDeviceDB.Host,
		cfg.WaDeviceDB.Port,
		cfg.WaDeviceDB.Dbname,
	)

	amocrmClient := AmocrmClient.New(
		cfg.Amocrm.BaseURL,
		cfg.Amocrm.ApiChatURL,
		cfg.Amocrm.Messenger,
		cfg.Amocrm.BotName,
		cfg.Amocrm.BotID,
		cfg.Amocrm.ChannelSecret,
		cfg.Amocrm.ChannelID,
		cfg.Amocrm.ChannelCode,
	)
	amocrmRepo := AmocrmSourceRepo.New(db)
	amocrmSourceService := AmocrmSourceService.New(amocrmRepo, amocrmClient)

	userbotRepo := UserbotRepo.New(db)
	userbotService := UserbotService.New(
		userbotRepo,
		amocrmSourceService,
		waDeviceDB,
		cfg.Logger.Type,
		"crmessenger-whatsapp",
	)

	userbotService.StartAll(context.Background())

	server.Run(
		db,
		amocrmSourceService,
		userbotService,
		cfg.Logger.Type,
		cfg.CRMessenger.CRMessengerWhatsapp.Port,
	)
}
