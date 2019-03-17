package tools

import (
	"encoding/json"
	"os"
	"skyfolk_services/configs"
)

func GetConfiguration() (configs.Configuration, error) {
	config := configs.Configuration{}
	file, err := os.Open("./configs/postgresql.json")

	if err != nil {
		return config, err
	}

	defer file.Close()

	decoder := json.NewDecoder(file)
	err = decoder.Decode(&config)

	if err != nil {
		return config, err
	}

	config.Server = GetEnv("DB_PORT_5432_TCP_ADDR", "localhost");
	config.Port = GetEnv("DB_PORT_5432_TCP_PORT", "5432");
	config.User = GetEnv("DB_ENV_POSTGRES_USER", "skyfolk");
	config.Password = GetEnv("DB_ENV_POSTGRES_PASSWORD", "skyf0lk_p4ssword@");
	config.Database = GetEnv("DB_ENV_DB", "skyfolk_db");

	return config, err
}

func GetEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}