package psql

import (
	"context"
	"database/sql"
	"fmt"
	_ "github.com/lib/pq"
	"log"
	"skyfolk_services/tools"
)

var ctx = context.Background()

func get() *sql.DB {
	config, err := tools.GetConfiguration()

	if err != nil {
		log.Fatalln(err)
	}

	dsn := fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable", config.User, config.Password, config.Server, config.Port, config.Database)

	db, err := sql.Open("postgres", dsn)

	if err != nil {
		log.Fatalln(err)

	}

	return db
}
