**Client** interactúa principalmente con el **NameNode** a través de API REST para operaciones como subir, bajar y listar archivos. La transferencia de datos (subir/bajar bloques) ocurre directamente entre el **Client** y los **DataNodes** usando **gRPC**.

# **Funciones del Client**

El cliente es responsable de interactuar con el sistema de archivos distribuidos mediante API REST para las operaciones de metadatos y gRPC para el envío de archivos reales.

## gRPC

- **write_file(path, data)**:
   - Solicita al NameNode la ubicación de los DataNodes para almacenar bloques.
   - Fragmenta el archivo en bloques y los envía a los DataNodes seleccionados utilizando gRPC en una pipeline.
   - Confirma con el NameNode la correcta replicación de los bloques.

- **read_file(path)**:
   - Solicita al NameNode la ubicación de los bloques replicados del archivo.
   - Lee los bloques directamente desde los DataNodes más cercanos utilizando gRPC.

- **hflush(path)**:
   - Envia todos los bloques pendientes de un archivo abierto en escritura y espera las confirmaciones de los DataNodes para asegurar la visibilidad de los datos escritos.

## REST

- **create_file(path)**: Solicita al NameNode crear un archivo vacío en el sistema de archivos con el nombre especificado.

- **delete_file(path)**: Solicita al NameNode eliminar el archivo del sistema.

- **append_file(path, data)**: Permite agregar más datos a un archivo existente solicitando al NameNode nuevos DataNodes para los bloques adicionales.

- **create_directory(path)**: Crea un directorio en el sistema solicitando al NameNode.

- **delete_directory(path)**: Elimina un directorio si está vacío.

- **list_directory(path)**: Solicita al NameNode una lista de archivos y directorios en el directorio especificado.

- **get_file_block_locations(path)**: Recupera las ubicaciones de los bloques del archivo desde el NameNode para fines de lectura.

### **Endpoints para el Client**

El cliente interactúa con el NameNode para recibir la ubicación de los DataNodes, y luego se comunica directamente con ellos para leer/escribir datos. Aquí están los endpoints clave:

#### **Subir un archivo (`/upload`)**
- **Método**: `POST`
- **Descripción**: El cliente inicia el proceso de subir un archivo solicitando al NameNode los DataNodes donde se almacenarán los bloques.
- **Conecta con**:
  - **NameNode**: `getDataNodesForWrite(fileName)` (API REST).
  - **DataNode**: `storeBlock(blockData)` (gRPC).

#### **Descargar un archivo (`/download`)**
- **Método**: `GET`
- **Descripción**: El cliente solicita los bloques de un archivo y los reconstruye. Primero pregunta al NameNode por la ubicación de los bloques.
- **Conecta con**:
  - **NameNode**: `getDataNodesForRead(fileName)` (API REST).
  - **DataNode**: `readBlock(blockID)` (gRPC).

#### **Listar archivos (`/ls`)**
- **Método**: `GET`
- **Descripción**: El cliente solicita una lista de archivos y directorios en el NameNode.
- **Conecta con**:
  - **NameNode**: `listFiles(directoryPath)` (API REST).

#### **Eliminar archivo (`/delete`)**
- **Método**: `DELETE`
- **Descripción**: El cliente solicita al NameNode eliminar un archivo y luego borra los bloques en los DataNodes.
- **Conecta con**:
  - **NameNode**: `removeFile(fileName)` (API REST).
  - **DataNode**: `deleteBlock(blockID)` (gRPC).

#### **Crear directorio (`/mkdir`)**
- **Método**: `POST`
- **Descripción**: El cliente crea un nuevo directorio en el sistema de archivos del NameNode.
- **Conecta con**:
  - **NameNode**: `createDirectory(directoryName)` (API REST).
