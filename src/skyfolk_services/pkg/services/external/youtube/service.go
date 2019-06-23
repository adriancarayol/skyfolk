package youtube

import (
	"time"
	"fmt"
	"skyfolk_services/pkg/cache"
	"log"
	"skyfolk_services/pkg/services/dao/psql"
	"strconv"
	"net/http"
	"encoding/json"
)

const YouTubeKey = "youtube_"

type YouTubeResult struct {
	Kind   string `json:"kind"`
	Items []Item `json:"items"`
}

type Item struct {
	Id string `json:"id"`
	ContentDetail ContentDetail `json:"contentDetails"`
}

type ContentDetail struct {
	RelatedPlaylists RelatedPlaylists `json:"relatedPlaylists"`
}

type RelatedPlaylists struct {
	Uploads string `json:"uploads"`
}

type PlayListResult struct {
	Items []ItemPlayList `json:"items"`
}

type ItemPlayList struct {
	Snippet Snippet `json:"snippet"`
}

type Snippet struct {
	Title	string `json:"title"`
	publishedAt string `json:"publishedAt"`
	Thumbnails Thumbnails `json:"thumbnails"`
	ResourceId ResourceId `json:"resourceId"`
}

type Thumbnails struct {
	Default DefaultThumbnail `json:"default"`
}

type DefaultThumbnail struct {
	URL string `json:"url"`
}

type ResourceId struct {
	VideoId string `json:"videoId"`
}

var myClient = &http.Client{Timeout: 10 * time.Second}

func getJson(url string, target interface{}, auth_token string) error {
	bearer := "Bearer " + auth_token
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Add("Authorization", bearer)

	r, err := myClient.Do(req)

	if err != nil {
		fmt.Println(err)
		return err
	}

	fmt.Println(r.StatusCode)
	defer r.Body.Close()
	return json.NewDecoder(r.Body).Decode(target)
}

func (youtube *YouTubeResult) SetYouTubeResults(data map[string]interface{}, id string, redis *cache.RedisClient) {
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

	url := "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true"

	youtubeResult := YouTubeResult{}
	getJson(url, &youtubeResult, userService.AuthToken)

	if len(youtubeResult.Items) <= 0 {
		fmt.Println("YouTube user without channels...")
		return
	}

	playListUrl := fmt.Sprintf("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=%s",
		youtubeResult.Items[0].ContentDetail.RelatedPlaylists.Uploads)

	playListResult := PlayListResult{}
	getJson(playListUrl, &playListResult, userService.AuthToken)

	json_result, err := json.Marshal(playListResult.Items)

	if err != nil {
		log.Printf("Cannot marshal youtube from ID %s", id)
		return
	}

	key := YouTubeKey + id
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
