package twitter

import (
	"encoding/json"
	"fmt"
	"github.com/ChimeraCoder/anaconda"
	"log"
	"net/url"
	"skyfolk_services/pkg/cache"
	"skyfolk_services/pkg/services/dao/psql"
	"skyfolk_services/tools"
	"strconv"
	"time"
)

const TwitterKey = "twitter_"

type TwitterResult struct {
	TwitterID   int64  `json:"twitterId"`
	UserAccount string `json:"userAccount"`
	ProfileURL  string `json:"profileURL"`
	FullText    string `json:"fullText"`
	Link        string `json:"link"`
	CreatedAt   string `json:"createAt"`
	MediaURLs	[]string `json:"media"`
}

var ConsumerKey = tools.GetEnv("TWITTER_CONSUMER_TOKEN", "ICxk7pSKDmUffHxEVyP2bqQ2l");

var ConsumerSecret = tools.GetEnv("TWITTER_CONSUMER_SECRET", "ptzwzgTHzR0jj2jrvibTgKnFTuPdICY2HBUeVCAgiTHREa2evR");

func (twitter *TwitterResult) GetAPI(auth_token string, auth_token_secret string) *anaconda.TwitterApi {
	api := anaconda.NewTwitterApiWithCredentials(auth_token,
		auth_token_secret,
		ConsumerKey,
		ConsumerSecret)
	return api
}

func (twitter *TwitterResult) Search(api *anaconda.TwitterApi, query string) []anaconda.Tweet {
	searchResult, err := api.GetSearch(query, nil)

	if err != nil {
		fmt.Println(err)
		return nil
	}

	return searchResult.Statuses
}

func (twitter *TwitterResult) GetTimelineByUser(api *anaconda.TwitterApi, account string) []anaconda.Tweet {
	v := url.Values{}
	v.Add("screen_name", account)
	searchResult, err := api.GetUserTimeline(v)

	if err != nil {
		fmt.Println(err)
		return nil
	}

	return searchResult
}

func (twitter *TwitterResult) SetTwitterResults(data map[string]interface{}, id string, redis *cache.RedisClient) {
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

	api := twitter.GetAPI(userService.AuthToken, userService.AuthTokenSecret)

	wordToSearch := widget_data["word_to_search"].(string)
	accountToSearch := widget_data["account_to_search"].(string)

	var timeline []anaconda.Tweet
	var searchResult []anaconda.Tweet

	if accountToSearch != "" {
		timeline = twitter.GetTimelineByUser(api, accountToSearch)
	}

	if wordToSearch != "" {
		searchResult = twitter.Search(api, wordToSearch)
	}

	api.Close()
	tweets := append(timeline[:], searchResult[:]...)
	twitter.InsertTweetsInRedis(id, tweets, redis)
}

func (twitter *TwitterResult) InsertTweetsInRedis(id string, statuses []anaconda.Tweet, redis *cache.RedisClient) {
	var tweets []TwitterResult

	for _, status := range statuses {
		entities := status.Entities
		var mediaUrls []string

		for _, media := range entities.Media {
			mediaUrls = append(mediaUrls, media.Media_url_https)
		}

		tweet := TwitterResult{TwitterID: status.Id,
			UserAccount: status.User.ScreenName, FullText: status.FullText,
			Link: status.Source, CreatedAt: status.CreatedAt, ProfileURL: status.User.URL, MediaURLs: mediaUrls}
		tweets = append(tweets, tweet)
	}

	result, err := json.Marshal(tweets)

	if err != nil {
		log.Printf("Cannot marshal tweets from ID %s", id)
		return
	}

	key := TwitterKey + id
	redis.SetValueByKey(key, string(result))
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
