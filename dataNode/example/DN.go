package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
    "time"
    "bytes"
)

// estructura DataNode que almacena la configuración del DataNode
type DataNode struct {
    OwnIP             string `json:"own_ip"`
    OwnPort           int    `json:"own_port"`
    BlockSize         int    `json:"block_size"`
    HeartbeatInterval int    `json:"heartbeat_interval"`
    BlockCheckInterval int   `json:"block_check_interval"`
    NameNodeIP        string `json:"namenode_ip"`
    NameNodePort      int    `json:"namenode_port"`
}

// función para cargar la configuración del DataNode desde el archivo JSON
func LoadConfig(filename string) (*DataNode, error) {
    data, err := ioutil.ReadFile(filename)
    if err != nil {
        return nil, err
    }

    var datanode DataNode
    err = json.Unmarshal(data, &datanode)
    if err != nil {
        return nil, err
    }
    return &datanode, nil
}

// función para registrar el DataNode en el NameNode
func (dn *DataNode) RegisterWithNameNode() error {
    url := fmt.Sprintf("http://%s:%d/register_datanode", dn.NameNodeIP, dn.NameNodePort)
    body := map[string]interface{}{
        "datanode_ip":   dn.OwnIP,
        "datanode_port": dn.OwnPort,
    }
    jsonData, _ := json.Marshal(body)

    resp, err := http.Post(url, "application/json", bytes.NewReader(jsonData))
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode == 200 {
        data, _ := ioutil.ReadAll(resp.Body)
        var response map[string]interface{}
        json.Unmarshal(data, &response)

        dn.BlockSize = int(response["block_size"].(float64))
        dn.HeartbeatInterval = int(response["heartbeat_interval"].(float64))
        dn.BlockCheckInterval = int(response["block_report_interval"].(float64))

        log.Println("DataNode registrado correctamente con el NameNode.")
        return nil
    }
    return fmt.Errorf("error al registrar DataNode")
}

// función para enviar heartbeats periódicos al NameNode
func (dn *DataNode) SendHeartbeat() {
    ticker := time.NewTicker(time.Duration(dn.HeartbeatInterval) * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        log.Println("Enviando heartbeat al NameNode...")
        url := fmt.Sprintf("http://%s:%d/heartbeat", dn.NameNodeIP, dn.NameNodePort)
        body := map[string]interface{}{
            "datanode_id": dn.OwnIP,
        }
        jsonData, _ := json.Marshal(body)
        http.Post(url, "application/json", bytes.NewReader(jsonData))
    }
}

// función para enviar block reports periódicos al NameNode
func (dn *DataNode) SendBlockReport() {
    ticker := time.NewTicker(time.Duration(dn.BlockCheckInterval) * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        log.Println("Enviando block report al NameNode...")
        url := fmt.Sprintf("http://%s:%d/block_report", dn.NameNodeIP, dn.NameNodePort)
        body := map[string]interface{}{
            "datanode_id":  dn.OwnIP,
            "block_list":   []string{"block1", "block2"}, // Aquí puedes agregar la lógica real
            "checksum_list": []string{"checksum1", "checksum2"},
        }
        jsonData, _ := json.Marshal(body)
        http.Post(url, "application/json", bytes.NewReader(jsonData))
    }
}
