package models

type ExternalServices struct {
	Id int
	AuthToken string
	ServiceId int
	UserId int
	AuthTokenSecret string
}
