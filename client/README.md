## **Client**

El **Client** es responsable de interactuar con el sistema de archivos distribuido. Utiliza API REST para coordinarse con el **NameNode** y obtener información sobre la ubicación de los bloques, crear/eliminar archivos o directorios, y solicitar metadatos de los archivos. Además, utiliza gRPC para transferir bloques de datos directamente a los **DataNodes** cuando se realizan operaciones de subida o descarga de archivos.

---

### **Endpoints API REST llamables por otros**

El **Client** no tiene endpoints API REST llamables por otros nodos. Todas las interacciones son iniciadas por el **Client** hacia el **NameNode** y los **DataNodes**.

---

### **Funciones gRPC ejecutables por otros**

El **Client** no tiene funciones gRPC ejecutables por otros nodos, ya que su función principal es iniciar solicitudes para leer y escribir bloques de archivos en los **DataNodes**.

---

### **Funciones propias del Client que llaman a otros nodos**

1. **Login (login)**
   - **Descripción**: Inicia sesión en el sistema, recibe un token de autenticación y el tamaño de bloque.
   - **Llama a**:
     - **NameNode** a través de `/login` (API REST).
   - **Parámetros**:
     - `username` (string): Nombre de usuario.
     - `password` (string): Contraseña.
   - **Retorno recibido**:
     - JSON con el token de autenticación y tamaño de bloque:
       ```json
       {"message": "Inicio de sesión exitoso", "token": "jwt_token", "block_size": 1048576}
       ```

2. **Registro de Cliente (register)**
   - **Descripción**: Registra un nuevo cliente en el sistema.
   - **Llama a**:
     - **NameNode** a través de `/register_client` (API REST).
   - **Parámetros**:
     - `username` (string): Nombre de usuario.
     - `password` (string): Contraseña.
   - **Retorno recibido**:
     - JSON con mensaje de éxito:
       ```json
       {"message": "Cliente registrado exitosamente"}
       ```

3. **Create File (put)**
   - **Descripción**: Solicita al **NameNode** la creación de un archivo vacío en el sistema de archivos.
   - **Llama a**:
     - **NameNode** a través de `/create_file` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del archivo que se va a crear.
     - `token` (string): Token de autenticación.
   - **Retorno recibido POR EL NAMENODE**:
     - JSON con la lista de bloques y sus ubicaciones:
       ```json
       {"blocks": [
         {"block_id": "block1_id", "datanode": {"ip": "ip1", "port": 5001}},
         {"block_id": "block2_id", "datanode": {"ip": "ip2", "port": 5001}},
         ...
       ]}
       ```
    - **Retorno recibido POR CADA DATANODE**:
      - Estructura de respuesta indicando éxito o error:
        ```json
        {"status": "Bloque almacenado exitosamente"}
        ```

4. **Read File (get)**
   - **Descripción**: Descarga un archivo del sistema distribuido, recuperando cada bloque desde los **DataNodes** y reensamblando el archivo.
   - **Llama a**:
     - **NameNode** a través de `/get_block_locations` (API REST) para obtener la lista de **DataNodes** que tienen los bloques del archivo.
     - **DataNode** a través de `read_block` (gRPC) para descargar los bloques desde los **DataNodes** correspondientes.
   - **Parámetros**:
     - `path` (string): La ruta del archivo que se va a leer.
     - `token` (string): Token de autenticación.
   - **Retorno recibido POR EL NAMENODE**:
     - JSON con la lista de bloques y sus ubicaciones:
       ```json
       {"blocks": [
         {"block_id": "block1_id", "datanode": {"ip": "ip1", "port": 5001}},
         {"block_id": "block2_id", "datanode": {"ip": "ip2", "port": 5001}},
         ...
       ]}
       ```
   - **Retorno recibido POR CADA DATANODE**:
      - Estructura de respuesta con los datos del bloque:
        ```json
        {"data": "binary_data"}
        ```

5. **Delete File (rm)**
   - **Descripción**: Elimina un archivo del sistema de archivos distribuido, tanto en el **NameNode** como en los **DataNodes**.
   - **Llama a**:
     - **NameNode** a través de `/delete_file` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del archivo que se va a eliminar.
     - `token` (string): Token de autenticación.
   - **Retorno recibido**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Archivo eliminado exitosamente"}
       ```

6. **Create Directory (mkdir)**
   - **Descripción**: Crea un nuevo directorio en el sistema de archivos distribuido.
   - **Llama a**:
     - **NameNode** a través de `/create_directory` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del directorio que se va a crear.
     - `token` (string): Token de autenticación.
   - **Retorno recibido**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Directorio creado exitosamente"}
       ```

7. **Delete Directory (rmdir)**
   - **Descripción**: Elimina un directorio y todo su contenido del sistema de archivos distribuido.
   - **Llama a**:
     - **NameNode** a través de `/delete_directory` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del directorio que se va a eliminar.
     - `token` (string): Token de autenticación.
   - **Retorno recibido**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Directorio y contenido eliminado exitosamente"}
       ```

8. **List Directory (ls)**
   - **Descripción**: Devuelve la lista de archivos y subdirectorios dentro de un directorio.
   - **Llama a**:
     - **NameNode** a través de `/list_directory` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del directorio que se va a listar.
     - `token` (string): Token de autenticación.
   - **Retorno recibido**:
     - JSON con la lista de archivos y directorios dentro del directorio:
       ```json
       {"contents": ["file1", "file2", "subdirectory"]}
       ```

9. **Change Directory (cd)**
   - **Descripción**: Cambia el directorio de trabajo actual.
   - **Llama a**:
     - Esta operación no necesita comunicación con el **NameNode**. Es manejada localmente por el **Client**.
   - **Parámetros**:
     - `path` (string): La ruta del directorio al que se desea cambiar.
   - **Retorno**:
     - Confirmación de cambio de directorio en el sistema local del cliente.
