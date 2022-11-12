package assets

import (
	"encoding/json"
	"os"
)

func Load() {}

func init() {
	configDir := os.Getenv("CONFIG_DIR")
	configFile := configDir + "assets.json"
	loadAssets(configFile)
}

type Asset struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
}

var assetsById map[int]*Asset
var assetsByName map[string]*Asset

func ById(id int) *Asset {
	return assetsById[id]
}
func ByName(name string) *Asset {
	return assetsByName[name]
}

func loadAssets(filePath string) {
	dat, err := os.ReadFile(filePath)
	if err != nil {
		panic(err)
	}
	var instances []Asset
	err = json.Unmarshal(dat, &instances)
	if err != nil {
		panic(err)
	}
	assetsById = make(map[int]*Asset)
	assetsByName = make(map[string]*Asset)
	for i, asset := range instances {
		assetsById[asset.Id] = &instances[i]
		assetsByName[asset.Name] = &instances[i]
	}
}
