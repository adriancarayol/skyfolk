package cache

import (
	"bytes"
	"compress/gzip"
	"github.com/go-redis/redis"
	"io/ioutil"
	"log"
	"skyfolk_services/tools"
	"time"
)

const TimeStamp = ":time"

type RedisStore interface {
	GetByKey(key string) (string, string, error)
	SetValueByKey(key string, value string) error
}

type RedisClient struct {
	*redis.Client
}

func InitRedisClient() (*RedisClient, error) {

	client := redis.NewClient(&redis.Options{
		Addr:     tools.GetEnv("REDIS_PORT_6379_TCP_ADDR", "localhost") + ":6379",
		Password: "",
		DB:       0,
	})

	_, err := client.Ping().Result()

	return &RedisClient{client}, err
}

func (redis *RedisClient) GetByKey(key string) (string, string, error) {
	timestampKey := key + TimeStamp

	result, err := redis.Get(key).Bytes()
	timestamp, err := redis.Get(timestampKey).Result()

	if err != nil {
		return "", "", err
	}

	rData := bytes.NewReader(result)

	r, err := gzip.NewReader(rData)

	if err != nil {
		log.Print("Cannot build gzip reader: ", err)
		return "", "", err
	}

	s, err := ioutil.ReadAll(r)

	if err != nil {
		log.Print("Cannot use ioutil.ReadAll: ", err)
		r.Close()
		return "", "", err
	}

	r.Close()

	return string(s), timestamp, err
}

func (redis *RedisClient) SetValueByKey(key string, value string) error {
	var b bytes.Buffer
	gz := gzip.NewWriter(&b)

	if _, err := gz.Write([]byte(value)); err != nil {
		log.Println(err)
		return err
	}

	if err := gz.Flush(); err != nil {
		log.Println(err)
		return err
	}

	if err := gz.Close(); err != nil {
		log.Println(err)
		return err
	}

	timestampKey := key + TimeStamp
	t := time.Now().Unix()

	err := redis.Set(key, b.Bytes(), 0).Err()

	if err == nil {
		err = redis.Set(timestampKey, t, 0).Err()
		if err != nil {
			redis.Del(key)
		}
	}

	return err
}
