package datanode

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"

	"github.com/MiguelCock/HDFS/dataNode/datanode/dngrcp"
	"google.golang.org/grpc"
)

type FileMetadata struct {
	Checksum string
	Size     int64
}

type DataNode struct {
	IP                 string `json:"own_ip"`
	Port               int    `json:"own_port"`
	NameNodeIP         string `json:"namenode_ip"`
	NameNodePort       int    `json:"namenode_port"`
	BlockSize          int    `json:"block_size"`
	HeartbeatInterval  int    `json:"heartbeat_interval"`
	BlockCheckInterval int    `json:"block_check_interval"`
	Files              map[string]FileMetadata
	dngrcp.UnimplementedDataNodeServiceServer
}

// ---------- CRETATE NEW DATA NODE ----------
func NewDataNode(filename string) *DataNode {
	var dn DataNode

	file, _ := os.Open(filename)
	defer file.Close()

	decoder := json.NewDecoder(file)

	decoder.Decode(&dn)

	dn.Files = make(map[string]FileMetadata)

	return &dn
}

// ---------- REGISTER THE DATA NODE TO THE NAME NODE ----------
func (dn *DataNode) register() error {
	url := fmt.Sprintf("http://%s:%d/register_datanode", dn.NameNodeIP, dn.NameNodePort)
	body := map[string]interface{}{
		"datanode_ip":   dn.IP,
		"datanode_port": dn.Port,
	}
	jsonData, _ := json.Marshal(body)

	resp, err := http.Post(url, "application/json", bytes.NewReader(jsonData))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return fmt.Errorf("error al registrar DataNode")
	}

	data, _ := io.ReadAll(resp.Body)
	var response map[string]interface{}
	json.Unmarshal(data, &response)

	dn.BlockSize = int(response["block_size"].(float64))
	dn.HeartbeatInterval = int(response["heartbeat_interval"].(float64))
	dn.BlockCheckInterval = int(response["block_report_interval"].(float64))

	log.Println("DataNode registrado correctamente con el NameNode.")
	return nil
}

// ============================== REST ==============================

// ---------- START REST SERVER ----------
func (dn *DataNode) StartRest() error {
	if err := dn.register(); err != nil {
		return err
	}

	go dn.heartBeat()
	go dn.blockReport()
	dn.checkSumVerification()

	http.HandleFunc("/delete_block/", dn.deleteBlock)
	http.HandleFunc("/replicatet_block/", dn.replicatetBlock)

	log.Println("Server starting on port 8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))

	return nil
}

// ============================== GRPC =============================

func (dn *DataNode) StartGRPC() {
	grpcPort := dn.Port + 1
	lis, err := net.Listen("tcp", fmt.Sprintf("%s:%d", dn.IP, grpcPort))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	server := grpc.NewServer()

	dngrcp.RegisterDataNodeServiceServer(server, dn)

	log.Printf("gRPC server running on %s:%d", dn.IP, grpcPort)
	if err := server.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
