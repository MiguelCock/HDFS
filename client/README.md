### **Funciones del Client**:
El cliente es responsable de interactuar con el sistema de archivos distribuidos mediante API REST para las operaciones de metadatos y gRPC para el envío de archivos reales.

- **create_file(path)**: Solicita al NameNode crear un archivo vacío en el sistema de archivos con el nombre especificado.
- **write_file(path, data)**: 
   - Solicita al NameNode la ubicación de los DataNodes para almacenar bloques.
   - Fragmenta el archivo en bloques y los envía a los DataNodes seleccionados utilizando gRPC en una pipeline.
   - Confirma con el NameNode la correcta replicación de los bloques.
- **read_file(path)**:
   - Solicita al NameNode la ubicación de los bloques replicados del archivo.
   - Lee los bloques directamente desde los DataNodes más cercanos utilizando gRPC.
- **delete_file(path)**: Solicita al NameNode eliminar el archivo del sistema.
- **append_file(path, data)**: Permite agregar más datos a un archivo existente solicitando al NameNode nuevos DataNodes para los bloques adicionales.
- **create_directory(path)**: Crea un directorio en el sistema solicitando al NameNode.
- **delete_directory(path)**: Elimina un directorio si está vacío.
- **list_directory(path)**: Solicita al NameNode una lista de archivos y directorios en el directorio especificado.
- **get_file_block_locations(path)**: Recupera las ubicaciones de los bloques del archivo desde el NameNode para fines de lectura.
- **hflush(path)**: Envia todos los bloques pendientes de un archivo abierto en escritura y espera las confirmaciones de los DataNodes para asegurar la visibilidad de los datos escritos.
