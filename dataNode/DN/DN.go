package DN

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
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
func (dn *DataNode) Register() error {
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

// ---------- DELETE BLOCK ----------
func (dn *DataNode) DeleteBlock(w http.ResponseWriter, r *http.Request) {
	filePath := strings.TrimPrefix(r.URL.Path, "/delete/")

	if filePath == "" {
		http.Error(w, "File path not provided", http.StatusBadRequest)
		return
	}

	if _, exist := dn.Files[filePath]; !exist {
		http.Error(w, "File Not found", http.StatusNotFound)
		return
	}

	os.Remove(filePath)

	delete(dn.Files, filePath)

	w.WriteHeader(http.StatusOK)
}

// ---------- BLOCK REPORT ----------
func (dn *DataNode) BlockReport() {
	ticker := time.NewTicker(time.Duration(dn.BlockCheckInterval) * time.Second)
	defer ticker.Stop()
	url := fmt.Sprintf("http://%s:%d/blockReport", dn.NameNodeIP, dn.NameNodePort)

	body := map[string]interface{}{
		"datanode_id":   dn.IP,
		"block_list":    []string{"block1", "block2"}, // Aquí puedes agregar la lógica real
		"checksum_list": []string{"checksum1", "checksum2"},
	}
	jsonData, _ := json.Marshal(body)

	resp, err := http.Post(url, "aplication/json", bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("Failed to send heartbeat request: %v", err)
	}

	log.Printf("Response Status: %s\n", resp.Status)

	resp.Body.Close()

}

// ---------- HEART BEAT ----------
func (dn *DataNode) HeartBeat() {
	ticker := time.NewTicker(time.Duration(dn.HeartbeatInterval) * time.Second)
	defer ticker.Stop()

	url := fmt.Sprintf("http://%s:%d/heartbeat", dn.NameNodeIP, dn.NameNodePort)

	body := map[string]interface{}{
		"datanode_id": dn.IP,
	}
	jsonData, _ := json.Marshal(body)

	resp, err := http.Post(url, "aplication/json", bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("Failed to send heartbeat request: %v", err)
	}

	log.Printf("Response Status: %s\n", resp.Status)

	resp.Body.Close()
}

// ---------- CHECK SUM ----------
func (dn *DataNode) CheckSumVerification() {}

// ---------- START REST SERVER ----------
func (n *DataNode) StartRest() error {
	if err := n.Register(); err != nil {
		return err
	}

	go n.HeartBeat()
	go n.BlockReport()
	n.CheckSumVerification()

	http.HandleFunc("/deleteBlock/", n.DeleteBlock)
	http.HandleFunc("/replicatetBlock/", n.ReplicatetBlock)

	log.Println("Server starting on port 8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))

	return nil
}

// ---------- REPLICATE BLOCK ----------
func (dn *DataNode) ReplicatetBlock(w http.ResponseWriter, r *http.Request) {
}

// ============================== GRPC =============================
func (n *DataNode) SaveBlock() {
}

func (n *DataNode) SendReport() {
}
