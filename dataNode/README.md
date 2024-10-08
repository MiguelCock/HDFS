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
     - `target_datanode_ip` (string): La IP del **DataNode** al que se replicará el bloque-
     - `target_datanode_port` (int): El puerto gRPC del **DataNode** al que se replicará el bloque.
   - **Retorno**:
     - JSON indicando éxito o error:

       ```json
       { "status": "Bloque replicado exitosamente" }
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
       { "status": "Bloque eliminado exitosamente" }
       ```

---

### **Funciones gRPC ejecutables por otros nodos**

1. **read_block**
   - **Descripción**: Proporciona los datos de un bloque almacenado en este **DataNode**.
   - **Es llamado por**: **Client**, cuando necesita leer los datos de un bloque.
   - **Parámetros**:
     - Estrucutra de petición **ReadBlockRequest**:
       - `block_id` (string): El identificador del bloque que se quiere leer.
   - **Retorno**:
     - Estructura de respuesta **ReadBlockResponse** con los datos del bloque:
        - `data` (binary): Los datos del bloque.
        - `status` (string): Mensaje de éxito o error.

2. **write_block**
   - **Descripción**: Almacena un bloque en este **DataNode**, enviado por un **Client**.
   - **Es llamado por**: **Client**, cuando está subiendo un archivo y necesita almacenar un bloque.
   - **Parámetros**:
     - Estrucutra de petición **WriteBlockRequest**:
       - `block_id` (string): El identificador del bloque.
       - `data` (binary): Los datos del bloque a almacenar.
   - **Retorno**:
     - Estructura de respuesta **WriteBlockResponse** indicando éxito o error:
       - `status` (string): Mensaje de éxito o error.

---

### **Funciones propias del Datanode que llaman a otros nodos**

1. **Register DataNode**
   - **Descripción**: Al iniciarse, el **DataNode** se registra en el **NameNode** para recibir el tamaño de bloque y los intervalos de heartbeats y block reports.
   - **Llama a**:
     - **NameNode** a través del endpoint `/register_datanode` (API REST).
   - **Parámetros**:
     - `datanode_ip` (string): La IP del **DataNode**.
     - `datanode_port` (int): El puerto del **DataNode**.
   - **En forma de**:
      ```json
      {
        "datanode_ip": "datanode_ip",
        "datanode_port": "datanode_port"
      }
      ```
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
     - `datanode_ip` (string): La ip de este **DataNode**.
     - `datanode_port` (int): El puerto del **DataNode**.
   - **En forma de**:
      ```json
      {
        "datanode_ip": "datanode_ip",
        "datanode_port": "datanode_port"
      }
      ```
   - **Retorno recibido**:
     - Ninguno.

3. **Block Report**
   - **Descripción**: Envía un informe de los bloques almacenados al **NameNode** y verifica su integridad usando checksums.
   - **Llama a**:
     - **NameNode** a través del endpoint `/block_report` (API REST).
   - **Parámetros**:
     - `datanode_ip` (string): La ip de ese **DataNode**.
     - `datanode_port` (int): El puerto del **DataNode**.
     - `block_list` (list): Lista de bloques almacenados.
     - `checksum_list` (list): Lista de checksums de los bloques.
     - **En forma de**:

        ```json
        {
          "datanode_ip": "datanode_ip",
          "datanode_port": "datanode_port",
          "blocks": [
            {"block_id": "block1_id", "checksum": "block1_checksum"},
            {"block_id": "block2_id", "checksum": "block2_checksum"},
            ...
          ]
        }
        ```
   - **Retorno recibido**: - Ninguno.
