# (HDFS) Sistema de Archivos Distribuidos por Bloques tipo Hadoop

## Estudiante(s): 
Esteban Vergara Giraldo, evergarag@eafit.edu.co  
Miguel Angel Cock Cano, macockc@eafit.edu.co  
Jonathan Betancur, jbetancur3@eafit.edu.co  

## Profesor: 
Alvaro Enrique Ospina SanJuan, aeospinas@eafit.edu.co  

---

## 1. Breve descripción

Este proyecto implementa un sistema de archivos distribuidos minimalista basado en bloques, inspirado en sistemas como GFS y HDFS. Utiliza una arquitectura compuesta por clientes, un NameNode y DataNodes, donde los archivos son divididos en bloques y distribuidos entre los DataNodes. El NameNode se encarga de la administración de metadatos, mientras que los clientes interactúan con él para obtener información sobre los bloques y transferir los datos a los DataNodes usando gRPC.

### 1.1. Aspectos cumplidos o desarrollados:

- Implementación de un sistema de archivos distribuido con separación de metadatos y almacenamiento de bloques.
- Manejo de archivos mediante operaciones comunes: crear, leer, eliminar archivos, y crear/eliminar directorios.
- Distribución de bloques en DataNodes con replicación básica.
- Clientes que interactúan con el sistema a través de una interfaz de comandos, similar a un shell, permitiendo realizar operaciones de archivos y directorios.
- Los bloques son transferidos a los DataNodes utilizando gRPC, mientras que los metadatos se gestionan mediante API REST.
- Implementación de heartbeat y block reports para asegurar la disponibilidad de los DataNodes y garantizar la consistencia de los bloques.

### 1.2. Aspectos NO cumplidos:

- No se implementó una solución para la recuperación automática de datos en caso de fallo completo del NameNode (no se implementó NameNode secundario).
- No se implementaron capas de seguridad avanzadas (como autenticación robusta o encriptación de datos).
- No se ha probado la solución en redes de gran escala con un número significativo de nodos y archivos.
  
---

## 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas

- **Arquitectura distribuida:** Inspirada en GFS y HDFS, con un NameNode centralizado para la gestión de metadatos y múltiples DataNodes que almacenan bloques de archivos.
- **API REST y gRPC:** Utilización de API REST para la comunicación entre el NameNode y los clientes, y gRPC para la transferencia eficiente de bloques entre los DataNodes y los clientes.
- **Replicación de datos:** Mecanismo básico de replicación para asegurar que cada bloque esté disponible en al menos dos DataNodes.
- **Heartbeat y Block Reports:** Cada DataNode envía informes periódicos sobre los bloques almacenados y heartbeats para asegurar que sigue operativo.
- **Cliente tipo consola:** El cliente puede ejecutar comandos similares a un shell como `put`, `get`, `rm`, `ls`, `mkdir`, `rmdir` y `cd`, interactuando con el NameNode y los DataNodes.

---

## 3. Descripción del ambiente de desarrollo y técnico

- **Lenguaje de programación:** 
  - Python (para el Cliente y NameNode).
  - Go (para los DataNodes).
  
- **Librerías y paquetes utilizados en Python:**
  - `Flask`: Para implementar la API REST en el NameNode.
  - `grpcio` y `grpcio-tools`: Para implementar la transferencia de archivos utilizando gRPC.
  - `requests`: Para manejar las peticiones HTTP desde los clientes hacia el NameNode.

- **Librerías utilizadas en Go:**
  - `net/http`: Para manejar peticiones REST desde los clientes y el NameNode.
  - `google.golang.org/grpc`: Para la transferencia de bloques entre clientes y DataNodes.

### Cómo se compila y ejecuta:

1. **Instalar dependencias en Python (Cliente y NameNode):**

   ```bash
   pip install -r requirements.txt
   ```

2. **Instalar dependencias en Go (DataNodes):**

   ```bash
   sudo apt-get install golang-go
   ```

3. **Compilar el archivo `.proto` para gRPC (si se hacen cambios en el archivo `.proto`):**

   - En Python:

     ```bash
     python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. datanode_service.proto
     ```

   - En Go:

     ```bash
     protoc --go_out=. --go-grpc_out=. datanode_service.proto
     ```

---

## 4. Configuración y despliegue en máquinas EC2

### PARA CONFIGURAR MÁQUINA EC2

#### Python (Client | NameNode):

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

#### Go (DataNode):

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

---

### Estructura de los archivos `bootstrap.json`

#### **NameNode**:

```json
{
    "own_ip": "172.31.94.180",
    "own_port": 5000,
    "block_size": 1048576,
    "heartbeat_interval": 5,
    "block_check_interval": 10,
    "replication_check_interval": 20
}
```

#### **Client y DataNode**:

```json
{
    "own_ip": "172.31.90.113",
    "own_port": 5000,
    "namenode_ip": "172.31.94.180",
    "namenode_port": 5000
}
```

---

### CAMBIAR BOOTSTRAP RÁPIDO DE MÁQUINA YA MONTADA

#### Usando el .sh:
```bash
./bootstrap.sh
```

#### Manualmente:
```bash
cd HDFS
cd <client|nameNode|dataNode>
git pull
sudo nano bootstrap.json
```

---

### INICIO RÁPIDO DE MÁQUINA YA MONTADA

#### Usando el .sh:
```bash
./run.sh
```

Este script desplegará un menú donde podrás seleccionar el tipo de nodo que deseas iniciar (Client, NameNode o DataNode).

#### Manualmente:

##### Python (Client | NameNode):
```bash
cd HDFS
cd <client|nameNode>
git pull
python3 main.py
```

##### Go (DataNode):
```bash
cd HDFS
cd dataNode
git pull
go build main.go
./main
```

---

### IPs:  

- **client1:** 172.31.90.113
- **client2:** 172.31.81.165
- **nameNode:** 172.31.94.180
- **dataNode1:** 172.31.92.212
- **dataNode2:** 172.31.83.103
- **dataNode3:** 172.31.88.165
- **dataNode4:** 172.31.82.61

> Las públicas también son permitidas y fueron probadas, pero usamos las privadas para no tener que cambiar el archivo `bootstrap.json` cada vez que se reinicia la máquina, ni asignar IPs estáticas a todos.

> Aún podríamos asignar una elástica para el namenode, si quieres probar que el uso de la IP pública funcione.

---

## 5. Descripción del ambiente de EJECUCIÓN (en producción)

- **Lenguaje de programación:**
  - Python (para Cliente y NameNode).
  - Go (para DataNodes).

### Cómo se lanza el sistema:

1. **Iniciar el sistema usando el menú interactivo:**
   ```bash
   ./run.sh
   ```

Este script desplegará un menú donde podrás seleccionar el tipo de nodo que deseas iniciar.

2. **Modificar el archivo `bootstrap.json`:**

   Si es necesario, modifica el archivo `bootstrap.json` con las IPs y puertos correspondientes a tu configuración.

---

## 6. Comandos del cliente

1. **Subir archivo (put):**
   ```bash
   put <ruta_del_archivo_local>
   ```

2. **Descargar archivo (get):**
   ```bash
   get <ruta_del_archivo_remoto>
   ```

3. **Eliminar archivo (rm):**
   ```bash
   rm <ruta_del_archivo_remoto>
   ```

4. **Listar directorios (ls):**
   ```bash
   ls
   ```

5. **Crear directorio (mkdir):**
   ```bash
   mkdir <nombre_directorio>
   ```

6. **Eliminar directorio (rmdir):**
   ```bash
   rmdir <nombre_directorio>
   ```

7. **Cambiar de directorio (cd):**
   ```bash
   cd <ruta_del_directorio>
   ```

8. **Salir (exit):**
   ```bash
   exit
   ```

---

## 7. Otra información relevante:

- **Replicación de bloques:** El sistema asegura que cada bloque esté almacenado en al menos dos DataNodes para garantizar la redundancia.
- **Pruebas en ambiente real:** El sistema ha sido desplegado y probado en instancias EC2 de AWS, simulando una red de nodos distribuidos con replicación de datos.


---

## 8. Fotos de la ejecución del sistema:

a

---

## 9. Video:

(Lo grabaremos el lunes y te lo mandaremos por el correo institucional)

---

## Referencias:

- **gRPC Documentation:** [https://grpc.io/docs/](https://grpc.io/docs/)
- **Flask Documentation:** [https://flask.palletsprojects.com/en/latest/](https://flask.palletsprojects.com/en/latest/)
- **Python Requests Documentation:** [https://docs.python-requests.org/en/master/](https://docs.python-requests.org/en/master/)
- **Go Documentation:** [https://golang.org/doc/](https://golang.org/doc/)
- **Hadoop Distributed File System (HDFS):** [https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html](https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html)
- **Google File System (GFS):** [https://research.google/pubs/pub51/](https://research.google/pubs/pub51/)
- **Red P2P del reto 1** [https://github.com/QuitoTactico/QuitoTactico-st0263](https://github.com/QuitoTactico/QuitoTactico-st0263)
