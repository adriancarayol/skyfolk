package tools

import (
	"encoding/json"
	"os"
	"skyfolk_services/src/configs"
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

	return config, err
}
