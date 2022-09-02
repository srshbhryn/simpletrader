package orderstates

import (
	"encoding/json"
	"os"
)

func Load() {}

func init() {
	configDir := os.Getenv("CONFIG_DIR")
	configFile := configDir + "orderstates.json"
	load(configFile)
}

type OrderState struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
}

var instanceById map[int]*OrderState
var instanceByName map[string]*OrderState

func ById(id int) *OrderState {
	return instanceById[id]
}
func ByName(name string) *OrderState {
	return instanceByName[name]
}

func load(filePath string) {
	dat, err := os.ReadFile(filePath)
	if err != nil {
		panic(err)
	}
	var instances []OrderState
	err = json.Unmarshal(dat, &instances)
	if err != nil {
		panic(err)
	}
	instanceById = make(map[int]*OrderState)
	instanceByName = make(map[string]*OrderState)
	for _, instance := range instances {
		instanceById[instance.Id] = &instance
		instanceByName[instance.Name] = &instance
	}
}
