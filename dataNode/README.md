## **DataNode**

El **DataNode** es responsable de almacenar bloques de datos, replicarlos y enviarlos a otros DataNodes o al Client a través de gRPC.

### **Endpoints API REST llamables por otros**

1. **`/delete_block`**
   - **Método**: DELETE
   - **Descripción**: Elimina un bloque almacenado en el DataNode.
   - **Es llamado por**: **NameNode**, cuando se ordena la eliminación de un bloque.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque a eliminar.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque eliminado"}
       ```

2. **`/replicate_block`**
   - **Método**: POST
   - **Descripción**: Replica un bloque hacia otro DataNode.
   - **Es llamado por**: **NameNode**, cuando el NameNode detecta que un bloque necesita replicación.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque a replicar.
     - `target_datanode` (string): El DataNode destino.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Replicación exitosa"}
       ```

3. **`/block_report`**
   - **Método**: POST
   - **Descripción**: Envía el reporte de los bloques almacenados al NameNode.
   - **Es llamado por**: **DataNode** mismo, periódicamente, para reportar al NameNode los bloques que almacena.
   - **Parámetros**:
     - `datanode_id` (string): El identificador del DataNode.
     - `block_list` (array): La

 lista de bloques almacenados.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Reporte enviado"}
       ```

### **Funciones GRPC ejecutables por otros**

1. **`StoreBlock`**
   - **Descripción**: Almacena un bloque enviado por el **Client**.
   - **Es llamado por**: **Client**, cuando el cliente sube un archivo y envía bloques al DataNode.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `data` (binary): El contenido del bloque.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque almacenado correctamente"}
       ```

2. **`ReadBlock`**
   - **Descripción**: Envía un bloque solicitado por el **Client**.
   - **Es llamado por**: **Client**, cuando el cliente descarga un archivo y solicita los bloques del DataNode.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
   - **Retorno**:
     - JSON con el contenido del bloque:
       ```json
       {"data": "contenido del bloque"}
       ```

### **Funciones propias que llaman a otros nodos**

1. **Replicación de bloques (`replicate_block`)**
   - **Llama a**:
     - **Otro DataNode** a través del endpoint `/store_block` (gRPC) para replicar un bloque.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `target_datanode` (string): El DataNode destino.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Replicación exitosa"}
       ```
