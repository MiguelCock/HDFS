import os
import requests
import grpc
import datanode_service_pb2
import datanode_service_pb2_grpc

class Client:
    def __init__(self, namenode_ip, namenode_port):
        self.namenode_ip = namenode_ip
        self.namenode_port = namenode_port
        self.token = None
        self.block_size = None
        self.current_directory = "/client/"

    def resolve_path(self, path):
        #normaliza la ruta proporcionada con respecto al directorio actual.
        if not path.startswith('/'):
            #si la ruta es relativa, la combinamos con el directorio actual
            path = os.path.join(self.current_directory, path)
        
        #normalizamos la ruta eliminando redundancias
        path = os.path.normpath(path)
        
        return path

    def login(self, username, password):
        #llamamos al API REST del NameNode para iniciar sesión y obtener un token
        response = requests.post(f'http://{self.namenode_ip}:{self.namenode_port}/login', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.block_size = data['block_size']
            print('Login successful')
        else:
            try:
                print(response.json()['message'])
            except:
                print('Login failed')

    def register(self, username, password):
        #llamamos al API REST del NameNode para registrar un nuevo usuario
        response = requests.post(f'http://{self.namenode_ip}:{self.namenode_port}/register_client', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            print('Registration successful')
        else:
            try:
                print(response.json()['message'])
            except:
                print('Registration failed')

    def logout(self):
        #llamamos al API REST del NameNode para cerrar sesión
        headers = {'Authorization': f'{self.token}'}
        response = requests.post(f'http://{self.namenode_ip}:{self.namenode_port}/logout', headers=headers)
        if response.status_code == 200:
            self.token = None
            print('Logout successful')
        else:
            try:
                print(response.json()['message'])
            except:
                print('Logout failed')

    def create_file(self, file_path, file_data):
        #solicitamos la creación de un archivo en el NameNode
        file_path = self.resolve_path(file_path)
        headers = {'Authorization': f'{self.token}'}
        size = len(file_data)
        response = requests.post(f'http://{self.namenode_ip}:{self.namenode_port}/create_file', json={
            'path': file_path,
            'size': size
        }, headers=headers)

        if response.status_code == 200:
            data = response.json()
            blocks = data['blocks']
            block_size = self.block_size
            for block in blocks:
                #dividimos el archivo en bloques para enviarlo
                start_index = (block['block_index'] - 1) * block_size
                end_index = min(start_index + block_size, size)
                block_data = file_data[start_index:end_index]
                print(f"Sending block {block['block_id']} to DataNode {block['datanodes'][0]['ip']}:{block['datanodes'][0]['port']+1}")
                self.send_block_to_datanode(block['datanodes'][0]['ip'], block['datanodes'][0]['port']+1, block['block_id'], block_data)
        else:
            try:
                print(response.json()['message'])
            except:
                print('File creation failed')

    def read_file(self, file_path):
        #llamamos al NameNode para obtener las ubicaciones de los bloques
        file_path = self.resolve_path(file_path)
        headers = {'Authorization': f'{self.token}'}
        response = requests.get(f'http://{self.namenode_ip}:{self.namenode_port}/get_block_locations', params={
            'path': file_path
        }, headers=headers)

        if response.status_code == 200:
            data = response.json()
            blocks = data['blocks']
            file_data = b''

            for block in blocks:
                block_data = None
                #intentamos leer el bloque desde todos los DataNodes disponibles
                for datanode in block['datanodes']:
                    block_data = self.read_block_from_datanode(datanode['ip'], datanode['port']+1, block['block_id'])
                    if block_data:  #si pudimos leer, salimos del bucle
                        break
                
                if block_data:
                    file_data += block_data
                else:
                    print(f"Failed to read block {block['block_id']} from all DataNodes")
                    return  #si no se pudo leer un bloque, cancelamos la operación de lectura completa

            #aquí escribimos el archivo a disco
            file_name = file_path.split('/')[-1]
            with open(f'downloaded_{file_name}', 'wb') as f:
                f.write(file_data)
            print('File downloaded successfully')
        else:
            try:
                print(response.json()['message'])
            except:
                print('File read failed')

    def send_block_to_datanode(self, datanode_ip, datanode_port, block_id, block_data):
        #usamos gRPC para enviar bloques a los DataNodes
        channel = grpc.insecure_channel(f'{datanode_ip}:{datanode_port}')
        stub = datanode_service_pb2_grpc.DataNodeServiceStub(channel)
        response = stub.WriteBlock(datanode_service_pb2.WriteBlockRequest(block_id=block_id, data=block_data))
        if response.status == "Bloque almacenado exitosamente":
            print(f"Block {block_id} sent successfully to {datanode_ip}:{datanode_port}")
        else:
            try:
                print(f"Failed to send block {block_id} to {datanode_ip}:{datanode_port}\nReason: {response.status}")
            except:
                print(f"Failed to send block {block_id} to {datanode_ip}:{datanode_port}")

    def read_block_from_datanode(self, datanode_ip, datanode_port, block_id):
        #usamos gRPC para leer un bloque de un DataNode
        channel = grpc.insecure_channel(f'{datanode_ip}:{datanode_port}')
        stub = datanode_service_pb2_grpc.DataNodeServiceStub(channel)
        response = stub.ReadBlock(datanode_service_pb2.ReadBlockRequest(block_id=block_id))
        
        #comprobamos si el bloque fue leído exitosamente
        if response.status == "Bloque leído exitosamente":
            return response.data
        else:
            try:
                print(f"Failed to read block {block_id} from {datanode_ip}:{datanode_port}\nReason: {response.status}")
            except:
                print(f"Failed to read block {block_id} from {datanode_ip}:{datanode_port}")
            return b''

    def delete_file(self, file_path):
        #llamamos al API REST para eliminar el archivo
        file_path = self.resolve_path(file_path)
        headers = {'Authorization': f'{self.token}'}
        response = requests.delete(f'http://{self.namenode_ip}:{self.namenode_port}/delete_file', params={
            'path': file_path
        }, headers=headers)
        if response.status_code == 200:
            print('File deleted successfully')
        else:
            try:
                print(response.json()['message'])
            except:
                print('File deletion failed')

    def create_directory(self, directory_path):
        #llamamos al API REST para crear un directorio
        directory_path = self.resolve_path(directory_path)
        headers = {'Authorization': f'{self.token}'}
        response = requests.post(f'http://{self.namenode_ip}:{self.namenode_port}/create_directory', json={
            'path': directory_path
        }, headers=headers)
        if response.status_code == 200:
            print('Directory created successfully')
        else:
            try:
                print(response.json()['message'])
            except:
                print('Directory creation failed')

    def delete_directory(self, directory_path):
        #llamamos al API REST para eliminar un directorio
        directory_path = self.resolve_path(directory_path)
        headers = {'Authorization': f'{self.token}'}
        response = requests.delete(f'http://{self.namenode_ip}:{self.namenode_port}/delete_directory', params={
            'path': directory_path
        }, headers=headers)
        if response.status_code == 200:
            print('Directory deleted successfully')
        else:
            try:
                print(response.json()['message'])
            except:
                print('Directory deletion failed')

    def list_directory(self, directory_path):
        #llamamos al API REST para listar los archivos dentro de un directorio
        directory_path = self.resolve_path(directory_path)
        headers = {'Authorization': f'{self.token}'}
        
        response = requests.get(f'http://{self.namenode_ip}:{self.namenode_port}/list_directory', params={
            'path': directory_path
        }, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print('Directory contents:')
            
            #procesamos las rutas completas para mostrar solo los nombres relativos
            for item in data['contents']:
                #obtenemos solo la parte relativa del nombre
                relative_path = item[len(directory_path):].strip('/')
                #mostramos directorios con '/'
                if item.endswith('/'):
                    print(f"{relative_path}/")
                else:
                    print(relative_path)
        else:
            try:
                print(response.json()['message'])
            except:
                print('Directory listing failed')

    def change_directory(self, directory_path):
        #verificar si el directorio existe antes de cambiar
        directory_path = self.resolve_path(directory_path)
        headers = {'Authorization': f'{self.token}'}
        response = requests.get(f'http://{self.namenode_ip}:{self.namenode_port}/list_directory', params={
            'path': directory_path
        }, headers=headers)

        if response.status_code == 200:
            if directory_path == '..':
                if self.current_directory != '/':
                    self.current_directory = '/'.join(self.current_directory.strip('/').split('/')[:-1])
                    if self.current_directory == '':
                        self.current_directory = '/'
                    else:
                        self.current_directory = '/' + self.current_directory + '/'
            else:
                self.current_directory = directory_path + '/' if not directory_path.endswith('/') else directory_path
            print(f'Changed directory to {self.current_directory}')
        else:
            print('Directory not found')
