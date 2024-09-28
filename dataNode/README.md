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
