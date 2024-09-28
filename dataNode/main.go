package main

import (
	"fmt"
	"log"

	"github.com/MiguelCock/HDFS/dataNode/datanode"
)

func main() {
	fmt.Print("STARTING SERVER")

	dn := datanode.NewDataNode("bootstrap.json")

	if err := dn.StartRest(); err != nil {
		log.Fatal(err)
	}

	dn.StartGRPC()
}
