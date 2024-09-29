package main

import (
	"fmt"
	"log"
	"github.com/MiguelCock/HDFS/dataNode/DN"
)

func main() {
	fmt.Print("STARTING SERVER")

	dn := datanode.NewDataNode("bootstrap.json")

	go func() {
		if err := dn.StartRest(); err != nil {
			log.Fatal(err)
		}
	}()

	go func() {
		if err := dn.StartGRPC(); err != nil {
			log.Fatal(err)
		}
	}()

	fmt.Println("Press Enter to exit...")
	fmt.Scanln()
	fmt.Println("Bye! :)")
}
