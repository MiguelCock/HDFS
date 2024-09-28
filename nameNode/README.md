## **NameNode**

El **NameNode** es responsable de administrar el espacio de nombres del sistema de archivos distribuido y de coordinar la ubicación de los bloques de datos. No almacena ni maneja directamente los bloques de datos, sino que gestiona los metadatos, indicando qué **DataNodes** contienen los bloques de un archivo.

---

### **Endpoints API REST llamables por otros nodos**

1. **/create_file**
   - **Método**: `POST`
   - **Descripción**: Crea un nuevo archivo en el sistema de archivos distribuidos.
   - **Es llamado por**: **Client**, cuando el usuario desea crear un archivo.
   - **Parámetros**:
     - `path` (string): La ruta completa del archivo.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Archivo creado exitosamente"}
       ```

2. **/delete_file**
   - **Método**: `DELETE`
   - **Descripción**: Elimina un archivo del sistema de archivos.
   - **Es llamado por**: **Client**, cuando el usuario desea eliminar un archivo.
   - **Parámetros**:
     - `path` (string): La ruta completa del archivo que se va a eliminar.
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
   - **Retorno**:
     - JSON con la lista de **DataNodes** donde se encuentran los bloques del archivo:
       ```json
       {"blocks": [
         {"block_id": "block1", "datanodes": ["datanode1", "datanode2"]},
         {"block_id": "block2", "datanodes": ["datanode3", "datanode4"]}
       ]}
       ```

---

### **Funciones gRPC ejecutables por otros nodos**

El **NameNode** no tiene funciones gRPC ejecutables por otros nodos. Toda la interacción se realiza a través de API REST.

---

### **Funciones propias del NameNode que llaman a otros nodos**

1. **Receive Block Report**
   - **Descripción**: Recibe un informe de los bloques almacenados en un **DataNode**.
   - **Llama a**:
     - **DataNode** a través del endpoint `/block_report` (API REST), cuando un **DataNode** informa sobre los bloques que está almacenando.
   - **Parámetros**:
     - `block_list` (list): Lista de bloques en el **DataNode**.
   - **Retorno**:
     - Ninguno.

2. **Replicate Block**
   - **Descripción**: Cuando el **NameNode** detecta que un bloque tiene menos de dos réplicas, selecciona otro **DataNode** y ordena la replicación.
   - **Llama a**:
     - **DataNode** a través del endpoint `/replicate_block` (API REST), para ordenar la replicación de un bloque a otro nodo.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `source_datanode` (string): El **DataNode** que actualmente almacena el bloque.
     - `target_datanode` (string): El **DataNode** al que se replicará el bloque.
   - **Retorno**:
     - Ninguno.
