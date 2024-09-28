## **NameNode**

El **NameNode** maneja la lógica de metadatos, la asignación de bloques y la replicación, interactuando con el **Client** y los **DataNodes** a través de API REST.

### **Endpoints API REST llamables por otros**

1. **`/assign_blocks`**
   - **Método**: POST
   - **Descripción**: Asigna DataNodes donde se deben almacenar los bloques de un archivo.
   - **Es llamado por**: **Client**, cuando quiere subir un archivo y necesita que el **NameNode** le asigne los DataNodes para almacenar los bloques.
   - **Parámetros**:
     - `file_name` (string): El nombre del archivo.
     - `num_blocks` (int): El número de bloques en los que se dividirá el archivo.
   - **Retorno**:
     - JSON con la lista de DataNodes asignados para cada bloque:
       ```json
       {
         "blocks": [
           {"block_id": "hash_part1", "data_nodes": ["datanode1", "datanode2"]},
           {"block_id": "hash_part2", "data_nodes": ["datanode1", "datanode3"]}
         ]
       }
       ```

2. **`/get_block_locations`**
   - **Método**: GET
   - **Descripción**: Devuelve las ubicaciones de los bloques de un archivo (los DataNodes que los almacenan).
   - **Es llamado por**: **Client**, cuando quiere descargar un archivo y necesita conocer la ubicación de los bloques.
   - **Parámetros**:
     - `file_name` (string): El nombre del archivo.
   - **Retorno**:
     - JSON con las ubicaciones de los bloques:
       ```json
       {
         "block_locations": [
           {"block_id": "hash_part1", "data_nodes": ["datanode1", "datanode2"]},
           {"block_id": "hash_part2", "data_nodes": ["datanode1", "datanode3"]}
         ]
       }
       ```

3. **`/delete_file`**
   - **Método**: DELETE
   - **Descripción**: Elimina los metadatos de un archivo y ordena la eliminación de los bloques en los DataNodes.
   - **Es llamado por**: **Client**, cuando el usuario desea eliminar un archivo del sistema.
   - **Parámetros**:
     - `file_name` (string): El nombre del archivo a eliminar.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Archivo eliminado correctamente"}
       ```

4. **`/list_directory`**
   - **Método**: GET
   - **Descripción**: Lista los archivos y directorios en un directorio dado.
   - **Es llamado por**: **Client**, cuando el usuario necesita ver la lista de archivos en un directorio.
   - **Parámetros**:
     - `directory_path` (string): La ruta del directorio.
   - **Retorno**:
     - JSON con la lista de archivos y directorios:
       ```json
       {
         "files": ["archivo1", "archivo2"],
         "directories": ["dir1", "dir2"]
       }
       ```

5. **`/create_directory`**
   - **Método**: POST
   - **Descripción**: Crea un nuevo directorio en el sistema.
   - **Es llamado por**: **Client**, cuando el usuario desea crear un nuevo directorio.
   - **Parámetros**:
     - `directory_path` (string): La ruta del nuevo directorio.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Directorio creado correctamente"}
       ```

6. **`/receive_block_report`**
   - **Método**: POST
   - **Descripción**: Recibe el reporte de bloques de los DataNodes.
   - **Es llamado por**: **DataNode**, cuando envía un reporte de los bloques que almacena.
   - **Parámetros**:
     - `datanode_id` (string): El identificador del DataNode.
     - `block_list` (array): La lista de bloques almacenados en el DataNode.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Reporte recibido"}
       ```

7. **`/heartbeat`**
   - **Método**: POST
   - **Descripción**: Recibe una señal de vida de un DataNode.
   - **Es llamado por**: **DataNode**, periódicamente para indicar que está operativo.
   - **Parámetros**:
     - `datanode_id` (string): El identificador del DataNode.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Heartbeat recibido"}
       ```

### **Funciones propias que llaman a otros nodos**

1. **Replicación de bloques (`replicate_block`)**
   - **Llama a**:
     - `/replicate_block` en **DataNode** (API REST): Ordena a un DataNode que replique un bloque a otro DataNode.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `source_datanode` (string): El DataNode fuente.
     - `target_datanode` (string): El DataNode destino.
   - **Retorno**:
     - JSON con el estado de la replicación:
       ```json
       {"status": "Replicación exitosa"}
       ```

2. **Asignación de bloques (`assign_blocks`)**
   - **Llama a**:
     - **Ninguno**, es un proceso interno.
   - **Descripción**: El NameNode asigna DataNodes para que el cliente pueda enviar los bloques de un archivo.
   - **Parámetros**:
     - `file_name` (string): El nombre del archivo.
     - `num_blocks` (int): El número de bloques del archivo.
   - **Retorno**:
     - JSON con la asignación de bloques y DataNodes:
       ```json
       {
         "blocks": [
           {"block_id": "hash_part1", "data_nodes": ["datanode1", "datanode2"]},
           {"block_id": "hash_part2", "data_nodes": ["datanode1", "datanode3"]}
         ]
       }
       ```
