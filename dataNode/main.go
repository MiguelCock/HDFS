package main

import (
	"fmt"

	"github.com/MiguelCock/HDFS/dataNode/DN"
)

func main() {
	fmt.Printf("STARTING SERVER")

	dn := DN.NewDataNode()
	dn.StartRest()
}
