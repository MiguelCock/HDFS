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
        self.current_directory = "/"

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
            print('Registration failed')

    #put
    def create_file(self, file_path, file_data):
        #solicitamos la creación de un archivo en el NameNode
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f'http://{self.namenode_ip}:{self.namenode_port}/create_file', json={
            'path': file_path
        }, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            blocks = data['blocks']
            for block in blocks:
                self.send_block_to_datanode(block['datanode']['ip'], block['datanode']['port'], block['block_id'], file_data)
        else:
            print('File creation failed')

    #get
    def read_file(self, file_path):
        #llamamos al NameNode para obtener las ubicaciones de los bloques
        #luego los recuperamos desde los DataNodes
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f'http://{self.namenode_ip}:{self.namenode_port}/get_block_locations', params={
            'path': file_path
        }, headers=headers)

        if response.status_code == 200:
            data = response.json()
            blocks = data['blocks']
            file_data = b''
            for block in blocks:
                file_data += self.read_block_from_datanode(block['datanode']['ip'], block['datanode']['port'], block['block_id'])
            print('File downloaded successfully')
            # Aquí puedes escribir el archivo a disco si lo deseas
        else:
            print('File read failed')

    def send_block_to_datanode(self, datanode_ip, datanode_port, block_id, block_data):
        #usamos gRPC para enviar bloques a los DataNodes
        channel = grpc.insecure_channel(f'{datanode_ip}:{datanode_port}')
        stub = datanode_service_pb2_grpc.DataNodeServiceStub(channel)
        response = stub.write_block(datanode_service_pb2.WriteBlockRequest(block_id=block_id, data=block_data))
        if response.status == "Bloque almacenado exitosamente":
            print(f"Block {block_id} sent successfully to {datanode_ip}:{datanode_port}")
        else:
            print(f"Failed to send block {block_id} to {datanode_ip}:{datanode_port}")

    def read_block_from_datanode(self, datanode_ip, datanode_port, block_id):
        #usamos gRPC para leer un bloque de un DataNode
        channel = grpc.insecure_channel(f'{datanode_ip}:{datanode_port}')
        stub = datanode_service_pb2_grpc.DataNodeServiceStub(channel)
        response = stub.read_block(datanode_service_pb2.ReadBlockRequest(block_id=block_id))
        return response.data

    def delete_file(self, file_path):
        #llamamos al API REST para eliminar el archivo
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.delete(f'http://{self.namenode_ip}:{self.namenode_port}/delete_file', params={
            'path': file_path
        }, headers=headers)
        if response.status_code == 200:
            print('File deleted successfully')
        else:
            print('File deletion failed')

    def create_directory(self, directory_path):
        #llamamos al API REST para crear un directorio
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f'http://{self.namenode_ip}:{self.namenode_port}/create_directory', json={
            'path': directory_path
        }, headers=headers)
        if response.status_code == 200:
            print('Directory created successfully')
        else:
            print('Directory creation failed')

    def delete_directory(self, directory_path):
        #llamamos al API REST para eliminar un directorio
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.delete(f'http://{self.namenode_ip}:{self.namenode_port}/delete_directory', params={
            'path': directory_path
        }, headers=headers)
        if response.status_code == 200:
            print('Directory deleted successfully')
        else:
            print('Directory deletion failed')

    def list_directory(self, directory_path):
        #llamamos al API REST para listar los archivos dentro de un directorio
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f'http://{self.namenode_ip}:{self.namenode_port}/list_directory', params={
            'path': directory_path
        }, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print('Directory contents:', data['contents'])
        else:
            print('Directory listing failed')

    def change_directory(self, directory_path):
        #cambiamos el directorio localmente sin llamar al NameNode
        self.current_directory = directory_path
        print(f'Changed directory to {self.current_directory}')

