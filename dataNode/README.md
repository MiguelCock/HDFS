**DataNode** se encarga de almacenar los bloques y replicarlos, utilizando gRPC para la transferencia de datos y API REST para coordinar con el **NameNode**.

# **Funciones del DataNode**

El DataNode almacena bloques de datos y realiza operaciones
de replicación y comunicación con otros DataNodes.

## gRPC

- **store_block(block_id, data)**:
  Almacena un bloque de datos en el sistema de archivos local.

- **send_block(block_id, target_datanode)**:
  Envía un bloque a otro DataNode utilizando gRPC para la replicación.

- **replicate_block(block_id, target_datanode)**:
  Replica un bloque a otro DataNode según la instrucción del NameNode.

## REST

- **delete_block(block_id)**:
  Elimina un bloque almacenado localmente cuando recibe la orden del NameNode.

- **block_report()**:
  Envía un informe periódico al NameNode sobre los bloques almacenados localmente.

- **heartbeat()**:
  Envía una señal periódica al NameNode para indicar que está operativo.

- **checksum_verification(block_id)**:
  Verifica la integridad de los bloques almacenados mediante checksums
  y notifica al NameNode en caso de corrupción.


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
