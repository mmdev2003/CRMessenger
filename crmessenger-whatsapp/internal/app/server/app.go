package server

import (
	"context"
	"crmessenger-whatsapp/internal/model"
	"crmessenger-whatsapp/pkg/validator"
	"github.com/labstack/echo/v4"
	"net/http"
)

import (
	amocrmHandler "crmessenger-whatsapp/internal/controller/http/handler/amocrm"
	userbotHandler "crmessenger-whatsapp/internal/controller/http/handler/userbot"
	httpMiddleware "crmessenger-whatsapp/internal/controller/http/middleware"
)

var PREFIX = "/api/whatsapp"

func Run(
	db model.IDB,
	amocrmSourceService model.IAmocrmSourceService,
	userbotService model.IUserbotService,
	loggerType,
	serverPort string,
) {
	server := echo.New()
	server.Validator = validator.New()

	includeHttpMiddleware(server, loggerType, PREFIX, "crmessenger-whatsapp")
	includeSystemHttpHandler(server, db)

	includeUserbotHandler(server, userbotService)
	includeAmocrmHandler(server, amocrmSourceService, userbotService)
	server.Logger.Fatal(server.Start(":" + serverPort))
}

func includeAmocrmHandler(
	server *echo.Echo,
	amocrmSourceService model.IAmocrmSourceService,
	userbotService model.IUserbotService,
) {
	server.POST(PREFIX+"/send/from/amocrm/:scope_id", amocrmHandler.SendMessageFromAmocrm(amocrmSourceService, userbotService))
	server.POST(PREFIX+"/amocrm-source/create", amocrmHandler.CreateAmocrmSource(amocrmSourceService))
}

func includeUserbotHandler(
	server *echo.Echo,
	userbotService model.IUserbotService,
) {
	server.POST(PREFIX+"/userbot/create", userbotHandler.CreateUserbot(userbotService))

}

func includeSystemHttpHandler(
	server *echo.Echo,
	db model.IDB,
) {
	server.GET(PREFIX+"/table/create", createTable(db))
	server.GET(PREFIX+"/table/drop", dropTable(db))
}

func includeHttpMiddleware(
	server *echo.Echo,
	loggerType,
	prefix,
	serviceName string,
) {
	server.Use(httpMiddleware.LoggerMiddleware(loggerType, prefix, serviceName))
}

func createTable(db model.IDB) echo.HandlerFunc {
	return func(request echo.Context) error {
		ctx := context.Background()

		err := db.CreateTable(ctx, model.CreateTable)
		if err != nil {
			return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
		}
		return request.JSON(http.StatusOK, "table created")
	}
}

func dropTable(db model.IDB) echo.HandlerFunc {
	return func(request echo.Context) error {
		ctx := context.Background()

		err := db.DropTable(ctx, model.DropTable)
		if err != nil {
			return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
		}

		return request.JSON(http.StatusOK, "table dropped")
	}
}
