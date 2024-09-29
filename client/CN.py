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
                self.send_block_to_datanode(block['datanode']['ip'], block['datanode']['port'], block['block_id'], block_data)
        else:
            try:
                print(response.json()['message'])
            except:
                print('File creation failed')

    def read_file(self, file_path):
        #llamamos al NameNode para obtener las ubicaciones de los bloques
        #luego los recuperamos desde los DataNodes
        headers = {'Authorization': f'{self.token}'}
        response = requests.get(f'http://{self.namenode_ip}:{self.namenode_port}/get_block_locations', params={
            'path': file_path
        }, headers=headers)

        if response.status_code == 200:
            data = response.json()
            blocks = data['blocks']
            file_data = b''
            for block in blocks:
                file_data += self.read_block_from_datanode(block['datanodes'][0]['ip'], block['datanodes'][0]['port'], block['block_id'])
            #Aquí puedes escribir el archivo a disco si lo deseas
            with open(f'downloaded_{file_path}', 'wb') as f:
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
        if response.status == "Bloque leído exitosamente":
            return response.data
        else:
            print(f"Failed to read block {block_id} from {datanode_ip}:{datanode_port}")
            return b''

    def delete_file(self, file_path):
        #llamamos al API REST para eliminar el archivo
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
        headers = {'Authorization': f'{self.token}'}
        response = requests.get(f'http://{self.namenode_ip}:{self.namenode_port}/list_directory', params={
            'path': directory_path
        }, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print('Directory contents:', data['contents'])
        else:
            try:
                print(response.json()['message'])
            except:
                print('Directory listing failed')

    def change_directory(self, directory_path):
        #verificamos si directory_path es una cadena vacía o contiene solo espacios en blanco
        if not directory_path.strip():
            print("Invalid directory path")
            return

        #normalizamos directory_path eliminando barras diagonales redundantes
        directory_path = directory_path.strip('/')

        #cambiamos el directorio localmente sin llamar al NameNode
        if directory_path == '..':
            if self.current_directory != '/':
                self.current_directory = '/'.join(self.current_directory.strip('/').split('/')[:-1])
                if self.current_directory == '':
                    self.current_directory = '/'
                else:
                    self.current_directory = '/' + self.current_directory + '/'
        else:
            if self.current_directory == '/':
                self.current_directory += directory_path
            else:
                self.current_directory += directory_path + '/'

        print(f'Changed directory to {self.current_directory}')
