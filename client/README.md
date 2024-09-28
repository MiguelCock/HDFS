## **Client**

El **Client** es el responsable de interactuar con el sistema de archivos distribuido. Utiliza API REST para coordinarse con el **NameNode** y obtener información sobre la ubicación de los bloques, crear/eliminar archivos o directorios, y solicitar metadatos de los archivos. Además, utiliza gRPC para transferir bloques de datos directamente a los **DataNodes** cuando se realizan operaciones de subida o descarga de archivos.

---

### **Endpoints API REST llamables por otros**

El **Client** no tiene endpoints API REST llamables por otros nodos. Todas las interacciones son iniciadas por el **Client** hacia el **NameNode** y los **DataNodes**.

---

### **Funciones gRPC ejecutables por otros**

El **Client** no tiene funciones gRPC ejecutables por otros nodos, ya que su función principal es iniciar solicitudes para leer y escribir bloques de archivos en los **DataNodes**.

---

### **Funciones propias del Client que llaman a otros nodos**

1. **Create File**
   - **Descripción**: Solicita al **NameNode** la creación de un archivo vacío en el sistema de archivos.
   - **Llama a**:
     - **NameNode** a través de `/create_file` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del archivo que se va a crear.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Archivo creado exitosamente"}
       ```

2. **Read File**
   - **Descripción**: Descarga un archivo del sistema distribuido, recuperando cada bloque desde los **DataNodes** y reensamblando el archivo.
   - **Llama a**:
     - **NameNode** a través de `/get_block_locations` (API REST) para obtener la lista de **DataNodes** que tienen los bloques del archivo.
     - **DataNode** a través de `read_block` (gRPC) para descargar los bloques desde los **DataNodes** correspondientes.
   - **Parámetros**:
     - `path` (string): La ruta del archivo que se va a leer.
   - **Retorno**:
     - Los datos del archivo reconstruido.

3. **Delete File**
   - **Descripción**: Elimina un archivo del sistema de archivos distribuido, tanto en el **NameNode** como en los **DataNodes**.
   - **Llama a**:
     - **NameNode** a través de `/delete_file` (API REST) para eliminar el archivo y los metadatos correspondientes.
     - **DataNode** a través de `delete_block` (gRPC) para eliminar los bloques del archivo en los **DataNodes**.
   - **Parámetros**:
     - `path` (string): La ruta del archivo que se va a eliminar.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Archivo eliminado exitosamente"}
       ```

4. **Create Directory**
   - **Descripción**: Crea un nuevo directorio en el sistema de archivos distribuido.
   - **Llama a**:
     - **NameNode** a través de `/create_directory` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del directorio que se va a crear.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Directorio creado exitosamente"}
       ```

5. **Delete Directory**
   - **Descripción**: Elimina un directorio vacío del sistema de archivos distribuido.
   - **Llama a**:
     - **NameNode** a través de `/delete_directory` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del directorio que se va a eliminar.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Directorio eliminado exitosamente"}
       ```

6. **List Directory**
   - **Descripción**: Devuelve la lista de archivos y subdirectorios dentro de un directorio.
   - **Llama a**:
     - **NameNode** a través de `/list_directory` (API REST).
   - **Parámetros**:
     - `path` (string): La ruta del directorio que se va a listar.
   - **Retorno**:
     - JSON con la lista de archivos y directorios dentro del directorio.
       ```json
       {"contents": ["file1", "file2", "subdirectory"]}
       ```
