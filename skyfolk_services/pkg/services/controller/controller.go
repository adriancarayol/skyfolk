package controller

import (
	"encoding/json"
	"fmt"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"skyfolk_services/pkg/cache"
	"skyfolk_services/pkg/services/external/twitter"
	"skyfolk_services/pkg/services/external/instagram"
	"skyfolk_services/pkg/services/models"
	"skyfolk_services/pkg/services/dao/psql"
	"strings"
	"skyfolk_services/pkg/services/external/youtube"
)

type Controller struct {
	redis *cache.RedisClient
}

func (controller *Controller) Redis() *cache.RedisClient {
	return controller.redis
}

func (controller *Controller) SetRedis(redis *cache.RedisClient) {
	controller.redis = redis
}

func (controller *Controller) GetServiceInfo(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]
	service := vars["service"]

	key := service + "_" + id
	result, timestamp, err := controller.redis.GetByKey(key)

	fmt.Println(timestamp)

	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
	} else {
		w.WriteHeader(http.StatusOK)
		w.Header().Set("Content-Type", "application/json")
	}

	json.NewEncoder(w).Encode(result)
}

func (controller *Controller) UpdateServiceInfo(w http.ResponseWriter, r *http.Request) {
	id := r.FormValue("id")
	log.Println("Get information for id: " + id)

	pinDAO := psql.PinImplPsql{}
	pin, err := pinDAO.GetById(id)

	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		log.Println("Not found pin with id %s", id)
		return
	}


	data, err := ParseJSON(err, pin, w)

	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		log.Fatalf("Cannot format data from pin with id %s", id)
		return
	}

	controller.SetResultsFromAPI(data, id)

	w.WriteHeader(http.StatusOK)
	w.Header().Set("Content-Type", "application/json")
}

func (controller *Controller) SetResultsFromAPI(data map[string]interface{}, id string) {
	fmt.Println(data)
	serviceName := strings.ToLower(fmt.Sprintf("%s", data["title"]))

	switch serviceName {
	case "twitter":
		twitterResult := twitter.TwitterResult{}
		twitterResult.SetTwitterResults(data, id, controller.redis)
	case "instagram":
		instagramResult := instagram.InstagramResult{}
		instagramResult.SetInstagramResults(data, id, controller.redis)
	case "youtube":
		youtubeResult := youtube.YouTubeResult{}
		youtubeResult.SetYouTubeResults(data, id, controller.redis)
	}
}

func ParseJSON(err error, pin models.Pin, w http.ResponseWriter) (map[string]interface{}, error) {
	var data map[string]interface{}

	err = json.Unmarshal([]byte(pin.PluginData), &data)

	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		log.Fatal("Unmarshal failed")
	}

	return data, err
}
