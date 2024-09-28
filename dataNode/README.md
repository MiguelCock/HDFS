## **DataNode**

El **DataNode** es el responsable de almacenar los bloques de datos y replicarlos según las instrucciones del **NameNode**. También envía informes periódicos sobre el estado de sus bloques y su disponibilidad al **NameNode**.

---

### **Endpoints API REST llamables por otros nodos**

1. **/replicate_block**
   - **Método**: `POST`
   - **Descripción**: Inicia la replicación de un bloque hacia otro **DataNode**, basado en la orden del **NameNode**.
   - **Es llamado por**: **NameNode**, cuando detecta que un bloque necesita replicarse.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `target_datanode` (string): El **DataNode** de destino para la replicación.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque replicado exitosamente"}
       ```

2. **/delete_block**
   - **Método**: `DELETE`
   - **Descripción**: Elimina un bloque almacenado en este **DataNode**.
   - **Es llamado por**: **NameNode**, cuando detecta que un bloque necesita eliminarse.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque que se va a eliminar.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque eliminado exitosamente"}
       ``` 

---

### **Funciones gRPC ejecutables por otros nodos**

1. **read_block**
   - **Descripción**: Proporciona los datos de un bloque almacenado en este **DataNode**.
   - **Es llamado por**: **Client**, cuando necesita leer los datos de un bloque.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque que se quiere leer.
   - **Retorno**:
     - Estructura de respuesta con los datos del bloque:
       ```json
       {"data": "binary_data"}
       ```

2. **write_block**
   - **Descripción**: Almacena un bloque en este **DataNode**, enviado por un **Client**.
   - **Es llamado por**: **Client**, cuando está subiendo un archivo y necesita almacenar un bloque.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `data` (binary): Los datos del bloque a almacenar.
   - **Retorno**:
     - Estructura de respuesta indicando éxito o error:
       ```json
       {"status": "Bloque almacenado exitosamente"}
       ```

---

### **Funciones propias del DataNode que llaman a otros nodos**

<<<<<<< HEAD
### **Endpoints para los DataNodes**

Los DataNodes manejan las operaciones de bloques reales, almacenando y replicando bloques de datos entre nodos.

#### **Almacenar un bloque (`/storeBlock`)**

- **Método**: `POST`
- **Descripción**: Almacena un bloque de datos en el DataNode.
- **Conecta con**:
  - **Client**: El cliente envía el bloque a través de gRPC.

#### **Leer un bloque (`/readBlock`)**

- **Método**: `GET`
- **Descripción**: Devuelve los datos del bloque solicitado.
- **Conecta con**:
  - **Client**: El cliente solicita el bloque a través de gRPC.

#### **Eliminar un bloque (`/deleteBlock`)**

- **Método**: `DELETE`
- **Descripción**: Elimina un bloque almacenado en el DataNode.
- **Conecta con**:
  - **NameNode**: Solicitud para eliminar el bloque.

#### **Reporte de bloques (`/getBlockReport`)**

- **Método**: `GET`
- **Descripción**: Envia un informe de los bloques almacenados en el DataNode al NameNode.
- **Conecta con**:
  - **NameNode**: Proporciona información de los bloques almacenados en este DataNode.

#### **Replica de bloques (`/replicateBlock`)**

- **Método**: `POST`
- **Descripción**: Replica un bloque de datos a otro DataNode para garantizar la replicación.
- **Conecta con**:
  - **DataNode**: gRPC para enviar el bloque a otro DataNode.
=======
1. **Register DataNode**
   - **Descripción**: Al iniciarse, el **DataNode** se registra en el **NameNode** para recibir el tamaño de bloque y los intervalos de heartbeats y block reports.
   - **Llama a**:
     - **NameNode** a través del endpoint `/register_datanode` (API REST).
   - **Parámetros**:
     - `datanode_ip` (string): La IP del **DataNode**.
     - `datanode_port` (int): El puerto del **DataNode**.
   - **Retorno recibido**:
     - JSON con el tamaño de bloque y los intervalos de heartbeat y block report:
       ```json
       {
         "block_size": 1048576,
         "heartbeat_interval": 5,
         "block_report_interval": 10
       }
       ```

2. **Heartbeat**
   - **Descripción**: Envía señales periódicas al **NameNode** para indicar que el **DataNode** está activo.
   - **Llama a**:
     - **NameNode** a través del endpoint `/heartbeat` (API REST).
   - **Parámetros**:
     - `datanode_id` (string): El identificador de este **DataNode**.
   - **Retorno recibido**:
     - Ninguno.

3. **Block Report**
   - **Descripción**: Envía un informe de los bloques almacenados al **NameNode** y verifica su integridad usando checksums.
   - **Llama a**:
     - **NameNode** a través del endpoint `/block_report` (API REST).
   - **Parámetros**:
     - `datanode_id` (string): El identificador de ese **DataNode**.
     - `block_list` (list): Lista de bloques almacenados.
     - `checksum_list` (list): Lista de checksums de los bloques.
   - **Retorno recibido**:
     - Ninguno.
>>>>>>> main
