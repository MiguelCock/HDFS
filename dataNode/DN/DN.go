package DN

import (
	"bytes"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"
)

type FileMetadata struct {
	Checksum string
	Size     int64
}

type DataNode struct {
	Files map[string]FileMetadata
}

// =============== REST ===============
func NewDataNode() *DataNode {
	return &DataNode{
		Files: make(map[string]FileMetadata),
	}
}

// ---------- DELETE BLOCK ----------
func (n *DataNode) DeleteBlock(w http.ResponseWriter, r *http.Request) {
	filePath := strings.TrimPrefix(r.URL.Path, "/delete/")

	if filePath == "" {
		http.Error(w, "File path not provided", http.StatusBadRequest)
		return
	}

	if _, exist := n.Files[filePath]; !exist {
		http.Error(w, "File Not found", http.StatusNotFound)
		return
	}

	os.Remove(filePath)

	delete(n.Files, filePath)

	w.WriteHeader(http.StatusOK)
}

// ---------- BLOCK REPORT ----------
func (n *DataNode) BlockReport() {
}

// ---------- HEART BEAT ----------
func (n *DataNode) HeartBeat() {
	url := "http://localhost:8080"

	data := []byte(`{"status":"alive"`)

	resp, err := http.Post(url, "/heartbeat", bytes.NewBuffer(data))
	if err != nil {
		log.Printf("Failed to send heartbeat request: %v", err)
	}
	defer resp.Body.Close()

	log.Printf("Response Status: %s\n", resp.Status)
}

// ---------- CHECK SUM ----------
func (n *DataNode) CheckSumVerification() {
}

// ---------- START REST SERVER ----------
func (n *DataNode) StartRest() {
	http.HandleFunc("/delete/", n.DeleteBlock)

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	go func() {
		for range ticker.C {
			n.HeartBeat()
		}
	}()

	log.Println("Server starting on port 8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))

	<-sigs
}

// =============== GRPC ==============
func (n *DataNode) SaveBlock() {
}

func (n *DataNode) SendReport() {
}

func (n *DataNode) ReplicatetBeat() {
}
