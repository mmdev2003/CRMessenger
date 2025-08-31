package logger

type ProdLogEntry struct {
	Lvl         string      `json:"lvl"`
	Msg         string      `json:"msg"`
	File        string      `json:"file"`
	DurationMs  int         `json:"duration_ms"`
	HttpStatus  int         `json:"http_status"`
	HttpPath    string      `json:"http_path"`
	HttpMethod  string      `json:"http_method"`
	RequestID   string      `json:"request_id"`
	ServiceName string      `json:"service_name"`
	Extra       interface{} `json:"extra,omitempty"`
}
