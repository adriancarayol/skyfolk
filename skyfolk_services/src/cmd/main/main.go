package main

import (
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"skyfolk_services/src/pkg/cache"
	"skyfolk_services/src/pkg/services/controller"
	"skyfolk_services/src/tools"
)

func main() {
	redisDB, err := cache.InitRedisClient()

	if err != nil {
		log.Fatal(err)
	}

	_, err = tools.GetConfiguration()

	if err != nil {
		log.Fatal("Cannot configure database")
	}

	apiController := &controller.Controller{}
	apiController.SetRedis(redisDB)

	router := mux.NewRouter()

	allowedHeaders := handlers.AllowedHeaders([]string{"X-Requested-With"})
	allowedOrigins := handlers.AllowedOrigins([]string{"*"})
	allowedMethods := handlers.AllowedMethods([]string{"GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS"})

	router.HandleFunc("/service/{service}/{id}", apiController.GetServiceInfo).Methods("GET")
	router.HandleFunc("/update/", apiController.UpdateServiceInfo).Methods("POST")
	http.ListenAndServe(":1800", handlers.CORS(allowedHeaders, allowedOrigins, allowedMethods)(router))

}
