package logger

import (
	"log/slog"
	"os"
)

func Setup(loggerType, rootPath string) {
	devHandler := &DevHandler{
		rootPath,
		slog.LevelDebug,
		os.Stdout,
		[]slog.Attr{},
	}

	logger := slog.New(devHandler)
	slog.SetDefault(logger)
}
