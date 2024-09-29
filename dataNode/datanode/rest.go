package datanode

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// -------------------- BLOCK REPORT --------------------
type FileChecksum struct {
	Block_id string `json:"block_id"`
	Checksum string `json:"checksum"`
}

func (dn *DataNode) blockReport() {
	ticker := time.NewTicker(time.Duration(dn.BlockCheckInterval) * time.Second)
	defer ticker.Stop()
	url := fmt.Sprintf("http://%s:%d/block_report", dn.NameNodeIP, dn.NameNodePort)

	var files []FileChecksum

	for block_id, metadata := range dn.Files {
		files = append(files, FileChecksum{
			Block_id: block_id,
			Checksum: metadata.Checksum,
		})
	}

	body := map[string]interface{}{
		"datanode_id": dn.IP,
		"blocks":      files,
	}

	jsonData, _ := json.Marshal(body)

	resp, err := http.Post(url, "aplication/json", bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("Failed to send heartbeat request: %v", err)
	}

	log.Printf("Response Status: %s\n", resp.Status)

	resp.Body.Close()

}

// -------------------- HEART BEAT --------------------
func (dn *DataNode) heartBeat() {
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

// -------------------- DELETE BLOCK --------------------
func (dn *DataNode) deleteBlock(w http.ResponseWriter, r *http.Request) {
	filePath := strings.TrimPrefix(r.URL.Path, "/delete_block/")

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

// -------------------- CHECK SUM --------------------
func (dn *DataNode) checkSumVerification(w http.ResponseWriter, r *http.Request) {}

// -------------------- REPLICATE BLOCK --------------------
func (dn *DataNode) replicatetBlock(w http.ResponseWriter, r *http.Request) {
}
