package instagram

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"skyfolk_services/src/pkg/cache"
	"skyfolk_services/src/pkg/services/dao/psql"
	"strconv"
	"time"
)

const InstagramKey = "instagram_"

type Data struct {
	Data []InstagramResult `json:"data"`
}

type InstagramResult struct {
	User      UserResult  `json:"user"`
	CreatedAt string      `json:"created_time"`
	Type      string      `json:"type"`
	Link      string      `json:"link"`
	Images    ImageResult `json:"images"`
}

type UserResult struct {
	ID             int64  `json:"id"`
	UserName       string `json:"username"`
	FullName       string `json:"full_name"`
	ProfilePicture string `json:"profile_picture"`
}

type ImageResult struct {
	LowResolution LowResolutionResult `json:"low_resolution"`
}

type LowResolutionResult struct {
	Width  int    `json:"width"`
	Height int    `json:"height"`
	Url    string `json:"url"`
}

var myClient = &http.Client{Timeout: 10 * time.Second}

func getJson(url string, target interface{}) error {
	r, err := myClient.Get(url)

	if err != nil {
		fmt.Println(err)
		return err
	}

	defer r.Body.Close()

	return json.NewDecoder(r.Body).Decode(target)
}

func (instagram *InstagramResult) SetInstagramResults(data map[string]interface{}, id string, redis *cache.RedisClient) {
	if !CheckIfNeedUpdate(redis, id) {
		return
	}

	if data == nil {
		log.Println("DATA is empty")
		return
	}

	widget_data := data["data"].(map[string]interface{})

	if widget_data == nil {
		log.Println("Widget data is empty")
		return
	}

	serviceId, ok := data["service"]

	if !ok {
		log.Println("Cannot get service id from service widget.")
		return
	}

	userServiceId := fmt.Sprint(serviceId)
	externalServiceDAO := psql.ExternalServicesImplPsql{}
	userService, err := externalServiceDAO.GetById(userServiceId)

	if err != nil {
		log.Println("Cannot retrieve user service with id: " + userServiceId)
		return
	}

	url := "https://api.instagram.com/v1/users/self/media/recent/?access_token=" + userService.AuthToken
	result := Data{}

	getJson(url, &result)
	json_result, err := json.Marshal(result.Data)

	if err != nil {
		log.Printf("Cannot marshal tweets from ID %s", id)
		return
	}

	key := InstagramKey + id
	redis.SetValueByKey(key, string(json_result))
}

func CheckIfNeedUpdate(redis *cache.RedisClient, id string) bool {
	result, timestamp, err := redis.GetByKey(id)

	i, err := strconv.ParseInt(timestamp, 10, 64)

	if err != nil {
		return true
	}

	if err != nil {
		return true
	}

	if result == "" {
		return true
	}

	if timestamp == "" {
		return true
	}

	date := time.Unix(i, 0)

	now := time.Now()

	diff := now.Sub(date)

	if diff.Minutes() <= 0 {
		return true
	}

	return false
}
