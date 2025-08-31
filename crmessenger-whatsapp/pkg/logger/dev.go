package logger

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"runtime"
	"strings"
)

type DevLogEntry struct {
	Lvl        string         `json:"lvl"`
	Msg        string         `json:"msg"`
	File       string         `json:"file"`
	DurationMs float64        `json:"duration_ms,omitempty"`
	HttpStatus int64          `json:"http_status,omitempty"`
	HttpPath   string         `json:"http_path,omitempty"`
	HttpMethod string         `json:"http_method,omitempty"`
	Extra      map[string]any `json:"extra,omitempty"`
}
type DevHandler struct {
	rootPath string
	minLevel slog.Leveler
	writer   io.Writer
	attrs    []slog.Attr
}

func (h *DevHandler) Enabled(_ context.Context, level slog.Level) bool {
	return level >= h.minLevel.Level()
}

func (h *DevHandler) Handle(_ context.Context, record slog.Record) error {
	file, _, line := h.getSourceLocation(record)

	logData := DevLogEntry{
		Lvl:  record.Level.String(),
		Msg:  record.Message,
		File: fmt.Sprintf("%s:%d", file, line),
	}

	for _, attr := range h.attrs {
		switch attr.Key {
		case "http_method":
			logData.HttpMethod = attr.Value.Any().(string)
		case "http_path":
			logData.HttpMethod = attr.Value.Any().(string)
		default:
			continue
		}
	}

	extra := make(map[string]any)
	record.Attrs(func(attr slog.Attr) bool {
		switch attr.Key {
		case "http_status":
			logData.HttpStatus = attr.Value.Any().(int64)
			return true
		case "duration_ms":
			logData.DurationMs = attr.Value.Any().(float64)
			return true
		default:
			extra[attr.Key] = attr.Value.Any()
			return true
		}
	})
	if len(extra) > 0 {
		logData.Extra = extra
	}

	jsonLogData, _ := json.Marshal(logData)
	_, err := h.writer.Write(append(jsonLogData, '\n'))
	return err
}
func (h *DevHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	return &DevHandler{
		rootPath: h.rootPath,
		minLevel: h.minLevel,
		writer:   h.writer,
		attrs:    attrs,
	}
}

func (h *DevHandler) WithGroup(name string) slog.Handler {
	return h
}

func (h *DevHandler) getSourceLocation(r slog.Record) (string, string, int) {
	frames := runtime.CallersFrames([]uintptr{r.PC})
	frame, _ := frames.Next()
	file := strings.TrimPrefix(frame.File, h.rootPath)
	funcName := frame.Function
	line := frame.Line

	return file, funcName, line
}
