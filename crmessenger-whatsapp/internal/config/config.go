package config

func New() *Config {
	return &Config{
		DB: DB{
			Username: "postgres",
			Dbname:   "postgres",
			Password: "postgres",
			Host:     "147.45.164.75",
			Port:     "10005",
		},
		WaDeviceDB: DB{
			Username: "postgres",
			Dbname:   "postgres",
			Password: "postgres",
			Host:     "147.45.164.75",
			Port:     "10015",
		},
		Amocrm: Amocrm{
			BaseURL:       ".amocrm.ru/api/v4",
			ApiChatURL:    "https://amojo.amocrm.ru/v2/origin/custom",
			Messenger:     "Whatsapp",
			BotName:       "Whatsapp",
			BotID:         "6c773699-ebbf-4523-b64b-9fe7279409c6",
			ChannelSecret: "05a49978df89d13417909498f4e168418db7a42c",
			ChannelID:     "f82092ec-9ce1-495a-a240-c125cfd98042",
			ChannelCode:   "ru.bngodev-test",
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
