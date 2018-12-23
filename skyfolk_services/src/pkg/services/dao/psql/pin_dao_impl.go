package psql

import (
	"database/sql"
	"fmt"
	"log"
	"skyfolk_services/src/pkg/services/models"
	"strconv"
)

type PinImplPsql struct {
}

func (dao PinImplPsql) GetAll() ([]models.Pin, error) {
	query := "SELECT id, plugin_data, user_id FROM dash_dashboardentry"
	pinList := make([]models.Pin, 0)
	db := get()
	defer db.Close()

	stmt, err := db.Prepare(query)

	if err != nil {
		return pinList, err
	}

	defer stmt.Close()

	rows, err := stmt.Query()

	if err != nil {
		return pinList, err
	}

	for rows.Next() {

		var row models.Pin
		err := rows.Scan(&row.Id, &row.PluginData, &row.UserId)

		if err != nil {
			fmt.Println(err)
			return nil, err
		}

		pinList = append(pinList, row)
	}

	return pinList, nil
}

func (dao PinImplPsql) GetById(id string) (models.Pin, error) {
	idToInt, err := strconv.Atoi(id)

	if err != nil {
		log.Println("Cannot convert id")
		return models.Pin{}, err
	}

	pin := models.Pin{}

	db := get()

	defer db.Close()

	err = db.QueryRowContext(ctx, "SELECT id, plugin_data, user_id FROM dash_dashboardentry WHERE id = $1",
		idToInt).Scan(&pin.Id, &pin.PluginData, &pin.UserId)

	switch {
	case err == sql.ErrNoRows:
		log.Printf("No pin with id %d", idToInt)
	case err != nil:
		log.Println(err)
	default:
		log.Printf("Get pin with id %d", idToInt)
	}

	return pin, err
}

func (dao PinImplPsql) Create() error {
	return nil
}
