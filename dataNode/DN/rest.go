package DN

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

// -------------------- BLOCK REPORT --------------------
type BlockChecksum struct {
	Block_id string `json:"block_id"`
	Checksum string `json:"checksum"`
}

func (dn *DataNode) blockReport() {
	ticker := time.NewTicker(time.Duration(dn.BlockCheckInterval) * time.Second)
	defer ticker.Stop()

	url := fmt.Sprintf("http://%s:%d/block_report", dn.NameNodeIP, dn.NameNodePort)

	for range ticker.C {
		var blocks []BlockChecksum

		for block_id, metadata := range dn.Blocks {
			blocks = append(blocks, BlockChecksum{
				Block_id: block_id,
				Checksum: metadata.Checksum,
			})
		}

		body := map[string]interface{}{
			"datanode_ip":   dn.IP,
			"datanode_port": dn.Port,
			"blocks":        blocks,
		}

		jsonData, _ := json.Marshal(body)

		resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			log.Printf("Failed to send block report request: %v", err)
			continue
		}

		defer resp.Body.Close()

		var respData map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&respData)
		if err != nil {
			log.Printf("Failed to decode response: %v", err)
			continue
		}

		if message, exists := respData["message"]; exists {
			log.Printf("NameNode message: %s", message)
		} else {
			log.Printf("Response Status: %s", resp.Status)
		}
	}
}

// -------------------- HEARTBEAT --------------------
func (dn *DataNode) heartBeat() {
	ticker := time.NewTicker(time.Duration(dn.HeartbeatInterval) * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		url := fmt.Sprintf("http://%s:%d/heartbeat", dn.NameNodeIP, dn.NameNodePort)

		body := map[string]interface{}{
			"datanode_ip":   dn.IP,
			"datanode_port": dn.Port,
		}
		jsonData, _ := json.Marshal(body)

		resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			log.Printf("Failed to send heartbeat request: %v", err)
			continue
		}

		defer resp.Body.Close()

		var respData map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&respData)
		if err != nil {
			log.Printf("Failed to decode response: %v", err)
			continue
		}

		if message, exists := respData["message"]; exists {
			log.Printf("NameNode message: %s", message)
		} else {
			log.Printf("Response Status: %s", resp.Status)
		}
	}
}


// -------------------- DELETE BLOCK --------------------
func (dn *DataNode) deleteBlock(w http.ResponseWriter, r *http.Request) {
	blockID := r.URL.Query().Get("block_id")

	if _, exist := dn.Blocks[blockID]; !exist {
		http.Error(w, "Block Not found", http.StatusNotFound)
		return
	}

	err := os.Remove(blockID)
	if err != nil {
		http.Error(w, "Failed to remove block file", http.StatusInternalServerError)
		return
	}

	delete(dn.Blocks, blockID)

	w.WriteHeader(http.StatusOK)
	response := Response{Status: "Bloque eliminado exitosamente"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
