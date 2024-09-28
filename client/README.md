## **Client**

El **Client** se conecta al **NameNode** para obtener metadatos sobre los archivos y a los **DataNodes** para subir y descargar bloques de archivos.

### **Funciones propias que llaman a otros nodos**

1. **Subir archivo (`write_file`)**
   - **Llama a**:
     - **NameNode** a través de `/assign_blocks` (API REST) para obtener los DataNodes donde almacenar los bloques.
     - **DataNode** a través de `StoreBlock` (gRPC) para subir los bloques de archivo.
   - **Parámetros**:
     - `file_name` (string): El nombre del archivo.
     - `file_data` (binary): El contenido del archivo.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Archivo subido correctamente"}
       ```

2. **Descargar archivo (`read_file`)**
   - **Llama a**:
     - **NameNode** a través de `/get_block_locations` (API REST) para obtener la ubicación de los bloques.
     - **DataNode** a través de `ReadBlock` (gRPC) para descargar los bloques.
   - **Parámetros**:
     - `file_name` (string): El nombre del archivo.
   - **Retorno**:
     - El contenido del archivo reconstruido a partir de los bloques.
