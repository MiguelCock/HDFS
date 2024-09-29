## **NameNode**

El **NameNode** es responsable de administrar el espacio de nombres del sistema de archivos distribuido y de coordinar la ubicación de los bloques de datos. No almacena ni maneja directamente los bloques de datos, sino que gestiona los metadatos, indicando qué **DataNodes** contienen los bloques de un archivo.

---

### **Endpoints API REST llamables por otros nodos**

1. **/create_file**
   - **Método**: `POST`
   - **Descripción**: El cliente sube un nuevo archivo al sistema de archivos distribuidos.
   - **Es llamado por**: **Client**, cuando el usuario desea crear un archivo.
   - **Parámetros**:
     - `path` (string): La ruta completa del archivo.
     - `size` (int): Tamaño en bytes del archivo.
     - `token` (string): Token de autenticación.
   - **Retorno**:
     - JSON con la lista de ips y puertos de los **DataNodes** al que **Client** debe mandarle los bloques del archivo:
       ```json
       {"blocks_quantity": 3,
        "blocks": [
         {"block_index": 1, "block_id": "block1_id", "datanode": {"ip": "ip1", "port": 5001}},
         {"block_index": 2, "block_id": "block2_id", "datanode": {"ip": "ip2", "port": 5001}},
         ...
       ]}
       ```

2. **/delete_file**
   - **Método**: `DELETE`
   - **Descripción**: Elimina un archivo del sistema de archivos.
   - **Es llamado por**: **Client**, cuando el usuario desea eliminar un archivo.
   - **Parámetros**:
     - `path` (string): La ruta completa del archivo que se va a eliminar.
     - `token` (string): Token de autenticación.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Archivo eliminado exitosamente"}
       ```

3. **/create_directory**
   - **Método**: `POST`
   - **Descripción**: Crea un nuevo directorio en el sistema de archivos.
   - **Es llamado por**: **Client**, cuando el usuario desea crear un directorio.
   - **Parámetros**:
     - `path` (string): La ruta completa del directorio que se va a crear.
     - `token` (string): Token de autenticación.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Directorio creado exitosamente"}
       ```

4. **/delete_directory**
   - **Método**: `DELETE`
   - **Descripción**: Elimina un directorio vacío en el sistema de archivos.
   - **Es llamado por**: **Client**, cuando el usuario desea eliminar un directorio.
   - **Parámetros**:
     - `path` (string): La ruta completa del directorio que se va a eliminar.
     - `token` (string): Token de autenticación.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Directorio eliminado exitosamente"}
       ```

5. **/list_directory**
   - **Método**: `GET`
   - **Descripción**: Lista los archivos y directorios dentro de un directorio.
   - **Es llamado por**: **Client**, cuando el usuario desea listar los contenidos de un directorio.
   - **Parámetros**:
     - `path` (string): La ruta completa del directorio.
     - `token` (string): Token de autenticación.
   - **Retorno**:
     - JSON con la lista de archivos y directorios:
       ```json
       {"contents": ["file1", "file2", "subdirectory"]}
       ```

6. **/get_block_locations**
   - **Método**: `GET`
   - **Descripción**: Devuelve la ubicación de los bloques de un archivo, indicando qué **DataNodes** contienen cada bloque.
   - **Es llamado por**: **Client**, cuando necesita leer un archivo y saber en qué **DataNodes** se encuentran los bloques.
   - **Parámetros**:
     - `path` (string): La ruta completa del archivo.
     - `token` (string): Token de autenticación.
   - **Retorno**:
     - JSON con la lista de **DataNodes** (y su info) donde se encuentran los bloques del archivo:
       ```json
       {"blocks_quantity": 3,
        "blocks": [
         {"block_index": 1, "block_id": "block1_id", "datanodes": [{"ip": "ip1", "port": 5001}, {"ip": "ip2", "port": 5001}]},
         {"block_index": 2, "block_id": "block2_id", "datanodes": [{"ip": "ip3", "port": 5001}, {"ip": "ip4", "port": 5001}]},
         ...
       ]}
       ```

7. **/block_report**
   - **Método**: `POST`
   - **Descripción**: Envía un informe al **NameNode** con los bloques almacenados en este **DataNode**.
   - **Es llamado por**: **DataNode** mismo (periódicamente).
   - **Parámetros**:
     - `datanode_id` (string): El identificador de ese **DataNode**.
     - `block_list` (list): Lista de los ids bloques almacenados en el **DataNode**.
     - `checksum_list` (list): Lista de checksums de los bloques para verificar la integridad.
     - **En forma de**

        ```json
        {"datanode_id": "datanode_id",
         "blocks": [
           {"block_id": "block1_id", "checksum":"block1_checksum"},
           {"block_id": "block2_id", "checksum":"block2_checksum"},
           ...
        ]}
        ```
   - **Retorno**:
     - Ninguno.

8. **/heartbeat**
   - **Método**: `POST`
   - **Descripción**: **DataNode** envía un heartbeat para informar que este sigue operativo.
   - **Es llamado por**: **DataNode** mismo (periódicamente).
   - **Parámetros**:
     - `datanode_id` (string): El identificador de ese **DataNode**.
   - **Retorno**:
     - Ninguno.

9. **/register_datanode**
   - **Método**: `POST`
   - **Descripción**: Registra el **DataNode** cuando se inicia, para recibir el tamaño de bloque y los retrasos para heartbeats y block reports.
   - **Es llamado por**: **DataNode** mismo al iniciarse.
   - **Parámetros**:
     - `datanode_ip` (string): La IP del **DataNode**.
     - `datanode_port` (int): El puerto del **DataNode**.
   - **Retorno**:
     - JSON con el tamaño de bloque y los tiempos de intervalo:
       ```json
       {
         "block_size": 1048576,
         "heartbeat_interval": 5,
         "block_report_interval": 10
       }
       ```

10. **/register_client**
    - **Método**: `POST`
    - **Descripción**: Registra un nuevo cliente en el sistema.
    - **Es llamado por**: **Client** al iniciar sesión.
    - **Parámetros**:
      - `username` (string): El nombre de usuario del cliente.
      - `password` (string): La contraseña del cliente.
    - **Retorno**:
      - JSON con el token de autenticación:
        ```json
        {"message": "Cliente registrado exitosamente"}
        ```

11. **/login**
    - **Método**: `POST`
    - **Descripción**: Inicia sesión de un cliente en el sistema.
    - **Es llamado por**: **Client** al iniciar sesión.
    - **Parámetros**:
      - `username` (string): El nombre de usuario del cliente.
      - `password` (string): La contraseña del cliente.
    - **Retorno**:
      - JSON con el token de autenticación:
        ```json
        {"message": "Inicio de sesión exitoso", "token": "jwt_token", "block_size": 1048576}
        ```

12. **/logout**
    - **Método**: `POST`
    - **Descripción**: Cierra sesión de un cliente en el sistema.
    - **Es llamado por**: **Client** al cerrar sesión.
    - **Parámetros**:
      - `token` (string): Token de autenticación.
    - **Retorno**:
      - JSON indicando éxito o error:
        ```json
        {"message": "Cierre de sesión exitoso"}
        ```

---

### **Funciones gRPC ejecutables por otros nodos**

El **NameNode** no tiene funciones gRPC ejecutables por otros nodos. Toda la interacción se realiza a través de API REST.

---

### **Funciones propias del NameNode que llaman a otros nodos**

1. **Delete Block**
   - **Descripción**: Cuando un archivo se elimina, el **NameNode** ordena a los **DataNodes** que eliminen los bloques correspondientes.
   - **Llama a**:
     - **DataNode** a través del endpoint `/delete_block` (API REST), para eliminar un bloque.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque que se va a eliminar.
   - **Retorno recibido**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque eliminado exitosamente"}
       ``` 

2. **Replicate Block**
   - **Descripción**: Cuando el **NameNode** detecta que un bloque tiene menos de dos réplicas, selecciona otro **DataNode** y ordena la replicación.
   - **Llama a**:
     - **DataNode** a través del endpoint `/replicate_block` (API REST), para ordenar la replicación de un bloque a otro nodo.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `target_datanode` (string): El **DataNode** al que se replicará el bloque, formato `ip:port`.
   - **Retorno recibido**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque replicado exitosamente"}
       ``` 
