### **Funciones del NameNode**:
El NameNode gestiona el sistema de archivos, la asignación de bloques y el control de la replicación.

- **assign_blocks(file, num_blocks)**: Determina qué DataNodes almacenarán los bloques de un archivo. El primer bloque va al nodo más cercano al cliente, y el segundo a un nodo aleatorio.
- **register_datanode(datanode)**: Registra un DataNode cuando se inicia y mantiene la lista de nodos activos.
- **get_block_locations(file)**: Devuelve una lista de los DataNodes que tienen réplicas de los bloques de un archivo.
- **delete_file(file)**: Elimina la referencia a un archivo y solicita a los DataNodes que borren los bloques correspondientes.
- **delete_block(block_id)**: Envía una instrucción a los DataNodes para eliminar un bloque específico.
- **heartbeat(datanode_id)**: Recibe señales periódicas de los DataNodes para confirmar que están activos.
- **replicate_block(block_id, source_datanode, target_datanode)**: Ordena la replicación de un bloque desde un DataNode a otro cuando la replicación es insuficiente.
- **receive_block_report(datanode_id, block_list)**: Recibe informes periódicos de los DataNodes sobre los bloques que almacenan.
- **check_replication(block_id)**: Verifica que todos los bloques del sistema tengan al menos dos réplicas, y ordena replicaciones si es necesario.
- **list_directory(path)**: Devuelve la lista de archivos y directorios en el sistema bajo el directorio especificado.
