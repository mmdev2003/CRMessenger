package config

func New() *Config {
	return &Config{
		DB: DB{
			Username: "",
			Dbname:   "",
			Password: "",
			Host:     "145.45.164.77",
			Port:     "10005",
		},
		WaDeviceDB: DB{
			Username: "",
			Dbname:   "",
			Password: "",
			Host:     "137.35.164.75",
			Port:     "10015",
		},
		Amocrm: Amocrm{
			BaseURL:       ".amocrm.ru/api/v4",
			ApiChatURL:    "https://amojo.amocrm.ru/v2/origin/custom",
			Messenger:     "Whatsapp",
			BotName:       "Whatsapp",
			BotID:         "",
			ChannelSecret: "",
			ChannelID:     "",
			ChannelCode:   "",
		},
		CRMessenger: CRMessenger{
			CRMessengerWhatsapp: Server{
				"crmessenger-whatsapp",
				"8005",
			},
		},
		Logger: Logger{
			"dev",
			"debug",
		},
	}
}

type Config struct {
	DB          DB
	WaDeviceDB  DB
	CRMessenger CRMessenger
	Amocrm      Amocrm
	Logger      Logger
}

type CRMessenger struct {
	CRMessengerWhatsapp Server
	CRMessengerAccount  Server
}

type DB struct {
	Username string
	Password string
	Host     string
	Port     string
	Dbname   string
}

type Amocrm struct {
	BaseURL       string
	ApiChatURL    string
	Messenger     string
	BotName       string
	BotID         string
	ChannelSecret string
	ChannelID     string
	ChannelCode   string
}

type Server struct {
	Host string
	Port string
}

type Logger struct {
	Type  string
	Level string
}
