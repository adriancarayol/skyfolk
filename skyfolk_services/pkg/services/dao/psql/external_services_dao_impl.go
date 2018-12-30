package psql

import (
	"database/sql"
	"log"
	"skyfolk_services/pkg/services/models"
	"strconv"
)

type ExternalServicesImplPsql struct {
}

func (dao ExternalServicesImplPsql) GetById(id string) (models.ExternalServices, error) {
	idToInt, err := strconv.Atoi(id)

	if err != nil {
		log.Println("Cannot convert id")
		return models.ExternalServices{}, err
	}

	externalService :=  models.ExternalServices{}

	db := get()

	defer db.Close()

	err = db.QueryRowContext(ctx, "SELECT id, auth_token, service_id, user_id, auth_token_secret FROM external_services_userservice WHERE id = $1",
		idToInt).Scan(&externalService.Id, &externalService.AuthToken, &externalService.ServiceId,
			&externalService.UserId, &externalService.AuthTokenSecret)

	switch {
	case err == sql.ErrNoRows:
		log.Printf("No user service with id %d", idToInt)
	case err != nil:
		log.Println(err)
	default:
		log.Printf("Get user service with id %d", idToInt)
	}

	return externalService, err
}
