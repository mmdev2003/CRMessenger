package userbot

import (
	"bytes"
	"context"
	"crmessenger-whatsapp/internal/model"
	"fmt"
	"github.com/skip2/go-qrcode"
	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/proto/waE2E"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	"google.golang.org/protobuf/proto"
	"image/png"
	"log/slog"
)

import (
	joinGroupHandler "crmessenger-whatsapp/internal/controller/wa/action"
	messageHandler "crmessenger-whatsapp/internal/controller/wa/message"
	messageMiddleware "crmessenger-whatsapp/internal/controller/wa/middleware"
)

func New(
	userbotRepo model.IUserbotRepo,
	amocrmSourceService model.IAmocrmSourceService,
	waDeviceDB *sqlstore.Container,
	loggerType,
	serviceName string,
) *ServiceUserbot {
	return &ServiceUserbot{
		userbotRepo:         userbotRepo,
		amocrmSourceService: amocrmSourceService,
		waDeviceDB:          waDeviceDB,
		userbots:            make(map[string]*whatsmeow.Client),
		loggerType:          loggerType,
		serviceName:         serviceName,
	}
}

type ServiceUserbot struct {
	userbotRepo         model.IUserbotRepo
	amocrmSourceService model.IAmocrmSourceService
	waDeviceDB          *sqlstore.Container
	userbots            map[string]*whatsmeow.Client
	loggerType          string
	serviceName         string
}

func (s *ServiceUserbot) CreateUserbot(ctx context.Context,
	accountID int,
) (*bytes.Buffer, error) {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)
	device := s.waDeviceDB.NewDevice()
	userbot := whatsmeow.NewClient(device, nil)

	qrChanForExport := make(chan string)
	go func() {
		qrCtx := context.Background()
		qrChan, _ := userbot.GetQRChannel(qrCtx)
		err := userbot.Connect()
		if err != nil {
			logger.Error(err.Error())
		}

		for evt := range qrChan {
			if evt.Event == "code" {
				qrChanForExport <- evt.Code
			} else {
				userbotWaPhoneNumber := device.GetJID().User
				userbot.AddEventHandler(
					messageMiddleware.LoggerMiddleware(
						messageHandler.EventMessageHandler(s.amocrmSourceService, userbotWaPhoneNumber),
						joinGroupHandler.JoinGroupChatHandler(s.amocrmSourceService, userbotWaPhoneNumber),
						s.loggerType,
						s.serviceName,
						userbotWaPhoneNumber,
					),
				)
				s.userbots[device.GetJID().User] = userbot
				err = s.userbotRepo.CreateUserbot(qrCtx, accountID, userbotWaPhoneNumber)
				if err != nil {
					logger.Error(err.Error())
				}
				logger.Info("Userbot создан",
					slog.String("userbotWaPhoneNumber", userbotWaPhoneNumber),
				)
			}
		}
	}()
	qrData := <-qrChanForExport

	qrCode, err := qrcode.New(qrData, qrcode.Medium)
	if err != nil {
		return nil, err
	}

	var qrBuffer bytes.Buffer
	err = png.Encode(&qrBuffer, qrCode.Image(256))
	if err != nil {
		return nil, err
	}

	return &qrBuffer, nil
}

func (s *ServiceUserbot) StartAll(ctx context.Context) {
	devices, err := s.waDeviceDB.GetAllDevices(ctx)
	if err != nil {
		fmt.Println(err)
	}
	for _, device := range devices {
		userbot := whatsmeow.NewClient(device, nil)

		err = userbot.Connect()
		if err != nil {
			fmt.Println(err)
		}
		userbotWaPhoneNumber := device.GetJID().User
		userbot.AddEventHandler(
			messageMiddleware.LoggerMiddleware(
				messageHandler.EventMessageHandler(s.amocrmSourceService, userbotWaPhoneNumber),
				joinGroupHandler.JoinGroupChatHandler(s.amocrmSourceService, userbotWaPhoneNumber),
				s.loggerType,
				s.serviceName,
				userbotWaPhoneNumber,
			),
		)
		s.userbots[userbotWaPhoneNumber] = userbot
		fmt.Println("Userbot запущен ", userbotWaPhoneNumber)

		if err != nil {
			fmt.Println(err)
		}
	}
}

func (s *ServiceUserbot) SendMessage(ctx context.Context,
	userbotWaPhoneNumber,
	contactWaPhoneNumber,
	text string,
) error {
	userbot := s.userbots[userbotWaPhoneNumber]
	message := &waE2E.Message{
		Conversation: proto.String(text),
	}
	var receiver types.JID
	if len(contactWaPhoneNumber) > 12 {
		receiver = types.NewJID(contactWaPhoneNumber, "s.whatsapp.net")
	} else {
		receiver = types.NewJID(contactWaPhoneNumber, "g.us")
	}

	_, err := userbot.SendMessage(ctx, receiver, message)
	if err != nil {
		return err
	}
	return nil
}
