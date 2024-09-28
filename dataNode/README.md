## **DataNode**

El **DataNode** es el responsable de almacenar los bloques de datos y replicarlos según las instrucciones del **NameNode**. También envía informes periódicos sobre el estado de sus bloques y su disponibilidad al **NameNode**.

---

### **Endpoints API REST llamables por otros nodos**

1. **/block_report**
   - **Método**: `POST`
   - **Descripción**: Envia un informe al **NameNode** con los bloques almacenados en este **DataNode**.
   - **Es llamado por**: **DataNode** mismo (periodicamente).
   - **Parámetros**:
     - `block_list` (list): Lista de los bloques almacenados en el **DataNode**.
   - **Retorno**:
     - Ninguno.

2. **/replicate_block**
   - **Método**: `POST`
   - **Descripción**: Inicia la replicación de un bloque hacia otro **DataNode**, basado en la orden del **NameNode**.
   - **Es llamado por**: **NameNode**, cuando detecta que un bloque necesita replicarse.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `target_datanode` (string): El **DataNode** de destino para la replicación.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque replicado exitosamente"}
       ```

---

### **Funciones gRPC ejecutables por otros nodos**

1. **read_block**
   - **Descripción**: Proporciona los datos de un bloque almacenado en este **DataNode**.
   - **Es llamado por**: **Client**, cuando necesita leer los datos de un bloque.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque que se quiere leer.
   - **Retorno**:
     - Los datos del bloque.

2. **write_block**
   - **Descripción**: Almacena un bloque en este **DataNode**, enviado por un **Client**.
   - **Es llamado por**: **Client**, cuando está subiendo un archivo y necesita almacenar un bloque.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque.
     - `data` (binary): Los datos del bloque a almacenar.
   - **Retorno**:
     - JSON indicando éxito o error:
       ```json
       {"status": "Bloque almacenado exitosamente"}
       ```

---

### **Funciones propias del DataNode que llaman a otros nodos**

1. **Heartbeat**
   - **Descripción**: Envía señales periódicas al **NameNode** para indicar que el **DataNode** está activo.
   - **Llama a**:
     - **NameNode** a través del endpoint `/heartbeat` (API REST).
   - **Parámetros**:
     - Ninguno.
   - **Retorno**:
     - Ninguno.

2. **Checksum Verification**
   - **Descripción**: Verifica la integridad de los bloques almacenados mediante checksums y notifica al **NameNode** si hay corrupción.
   - **Llama a**:
     - **NameNode** a través del endpoint `/block_report` (API REST), cuando se detecta que un bloque está corrupto.
   - **Parámetros**:
     - `block_id` (string): El identificador del bloque corrupto.
   - **Retorno**:
     - Ninguno.

