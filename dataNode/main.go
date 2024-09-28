package main

import (
	"fmt"
	"log"

	"github.com/MiguelCock/HDFS/dataNode/DN"
)

func main() {
	fmt.Printf("STARTING SERVER")

	dn := DN.NewDataNode("bootstrap.json")
	if err := dn.StartRest(); err != nil {
		log.Fatal(err)
	}
}
