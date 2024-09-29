## PARA CONFIGURAR MÁQUINA EC2 

### (Python: Client | NameNode):
```bash
sudo apt-get update
sudo apt-get install git
sudo apt-get install python3-pip
git clone https://github.com/MiguelCock/HDFS
cd HDFS
sudo pip3 install --break-system-packages -r requirements.txt
sudo chmod +x run.sh
sudo chmod +x bootstrap.sh
```

### (Go: DataNode):
```bash
sudo apt-get update
sudo apt-get install git
sudo apt-get install golang-go
git clone https://github.com/MiguelCock/HDFS
cd HDFS
echo "export GOPATH=$HOME/go" >> ~/.bashrc
echo "export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin" >> ~/.bashrc
source ~/.bashrc
sudo chmod +x run.sh
sudo chmod +x bootstrap.sh
```

## CAMBIAR BOOTSTRAP RÁPIDO DE MÁQUINA YA MONTADA:

### Usando el .sh
```bash
./bootstrap.sh
```

### Manualmente
```bash
cd HDFS
cd <client|nameNode|dataNode>
git pull
sudo nano bootstrap.json
```

## INICIO RÁPIDO DE MÁQUINA YA MONTADA 

### Usando el .sh
```bash
./run.sh
```

### Manualmente

#### (Python: Client | NameNode):
```bash
cd HDFS
cd <client|nameNode>
git pull
python3 main.py
```

#### (Go: DataNode):
```bash
cd HDFS
cd dataNode
git pull
go build main.go
./main
```

## IPs:  

**client1:** 
172.31.90.113

**client2:** 
172.31.81.165

**nameNode:** 
172.31.94.180

**dataNode1:** 
172.31.92.212

**dataNode2:** 
172.31.83.103

**dataNode3:** 
172.31.88.165

**dataNode4:** 
172.31.82.61
