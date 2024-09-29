import json
from flask import Flask, request, jsonify
import hashlib
import random
import requests

class NameNode:
    def __init__(self, bootstrap_path):
        #cargamos configuración desde el archivo bootstrap.json
        with open(bootstrap_path, 'r') as f:
            config = json.load(f)

        self.app = Flask(__name__)
        self.own_ip = config['own_ip']
        self.own_port = config['own_port']
        self.block_size = config['block_size']  #tamaño de bloque desde el bootstrap
        self.heartbeat_interval = config['heartbeat_interval']  #intervalo de heartbeat desde el bootstrap
        self.block_check_interval = config['block_check_interval']  #intervalo de verificación de bloques

        self.filesystem = {}  #diccionario para gestionar archivos y directorios
        self.block_locations = {}  #diccionario para rastrear la ubicación de bloques
        self.clients = {}  #diccionario para los clientes registrados
        self.tokens = {}  #diccionario para los tokens de los clientes logeados en el sistema
        self.datanodes = {}  #diccionario para los DataNodes registrados

        #inicializamos las rutas del API REST
        self.define_routes()

    def generate_user_token(self, username, password):
        #concatenamos el nombre de usuario y la contraseña
        text_to_hash = f"{username}|{password}"
        #calculamos el hash de 16 bits
        hash_object = hashlib.md5(text_to_hash.encode())
        return hash_object.hexdigest()[:16]
    
    def generate_block_id(self, file_path, part_number):
        #concatenamos la ruta completa con la parte correspondiente
        text_to_hash = f"{file_path}.part{part_number}"
        #calculamos el hash de 16 bits
        hash_object = hashlib.md5(text_to_hash.encode())
        return hash_object.hexdigest()[:16]
    
    def define_routes(self):
        #definimos las rutas de los endpoints


        @self.app.route('/register_client', methods=['POST'])
        def register_client():
            #registramos un nuevo cliente
            data = request.json
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({"message": "missing username or password"}), 400

            if username in self.clients:
                return jsonify({"message": "client already registered"}), 400

            self.clients[username] = password
            return jsonify({"message": "client registered successfully"}), 200

        @self.app.route('/login', methods=['POST'])
        def login():
            #iniciamos sesión de un cliente y retornamos un token
            data = request.json
            username = data.get('username')
            password = data.get('password')

            if username not in self.clients or self.clients[username] != password:
                return jsonify({"message": "invalid credentials"}), 401
            
            token = self.generate_user_token(username, password)

            if token in self.tokens:
                return jsonify({"message": "client already logged in"}), 400

            self.tokens[token] = username
            return jsonify({"message": "login successful", "token": token, "block_size": self.block_size}), 200
        
        @self.app.route('/logout', methods=['POST'])
        def logout():
            #cerramos la sesión de un cliente y eliminamos el token
            token = request.headers.get('Authorization')
            if token not in self.tokens:
                return jsonify({"message": "unauthorized"}), 401

            del self.tokens[token]
            return jsonify({"message": "logout successful"}), 200

        @self.app.route('/create_file', methods=['POST'])
        def create_file():
            #creamos un archivo nuevo en el sistema
            token = request.headers.get('Authorization')
            if token not in self.tokens:
                return jsonify({"message": "unauthorized"}), 401

            data = request.json
            path = data.get('path')
            size = data.get('size')

            if not path or not size:
                return jsonify({"message": "missing file path or size"}), 400

            if path in self.filesystem:
                return jsonify({"message": "file already exists"}), 400

            #calculamos la cantidad de bloques
            blocks_quantity = (size // self.block_size) + (1 if size % self.block_size != 0 else 0)
            blocks = []

            for i in range(blocks_quantity):
                #seleccionamos un DataNode aleatoriamente
                selected_datanode = random.choice(list(self.datanodes.values()))
                
                #generamos el block_id utilizando el hash de la ruta del archivo concatenado con .partN
                block_id = self.generate_block_id(path, i + 1)
                
                block = {
                    "block_index": i + 1,
                    "block_id": block_id,
                    "datanode": {
                        "ip": selected_datanode['ip'],
                        "port": selected_datanode['port']
                    }
                }
                blocks.append(block)

            #almacenamos la información del archivo
            self.filesystem[path] = blocks
            self.block_locations[path] = blocks

            return jsonify({"blocks_quantity": blocks_quantity, "blocks": blocks}), 200

        @self.app.route('/delete_file', methods=['DELETE'])
        def delete_file():
            #eliminamos un archivo del sistema
            token = request.headers.get('Authorization')
            if token not in self.tokens:
                return jsonify({"message": "unauthorized"}), 401

            path = request.args.get('path')

            if not path:
                return jsonify({"message": "missing file path"}), 400

            if path not in self.filesystem:
                return jsonify({"message": "file not found"}), 404

            #obtenemos la lista de bloques del archivo
            blocks = self.filesystem[path]

            #para cada bloque, contactamos a cada DataNode implicado y le pedimos que elimine el bloque
            for block in blocks:
                for datanode in block['datanodes']:
                    datanode_ip = datanode['ip']
                    datanode_port = datanode['port']
                    block_id = block['block_id']
                    url = f"http://{datanode_ip}:{datanode_port}/delete_block"
                    try:
                        response = requests.delete(url, params={"block_id": block_id})
                        if response.status_code == 200:
                            print(f"Block {block_id} deleted from DataNode {datanode_ip}:{datanode_port}")
                        else:
                            print(f"Failed to delete block {block_id} from DataNode {datanode_ip}:{datanode_port}")
                    except Exception as e:
                        print(f"Error contacting DataNode {datanode_ip}:{datanode_port}: {e}")

            #eliminamos el archivo del sistema después de haber eliminado todos los bloques
            del self.filesystem[path]
            del self.block_locations[path]

            return jsonify({"message": "file deleted successfully"}), 200

        @self.app.route('/create_directory', methods=['POST'])
        def create_directory():
            #creamos un directorio nuevo en el sistema
            token = request.headers.get('Authorization')
            if token not in self.tokens:
                return jsonify({"message": "unauthorized"}), 401

            data = request.json
            path = data.get('path')

            if not path:
                return jsonify({"message": "missing directory path"}), 400

            if path in self.filesystem:
                return jsonify({"message": "directory already exists"}), 400

            self.filesystem[path] = "directory"

            return jsonify({"message": "directory created successfully"}), 200

        @self.app.route('/delete_directory', methods=['DELETE'])
        def delete_directory():
            #eliminamos un directorio del sistema
            token = request.headers.get('Authorization')
            if token not in self.tokens:
                return jsonify({"message": "unauthorized"}), 401

            path = request.args.get('path')

            if not path:
                return jsonify({"message": "missing directory path"}), 400

            if path not in self.filesystem or self.filesystem[path] != "directory":
                return jsonify({"message": "directory not found"}), 404

            del self.filesystem[path]
            return jsonify({"message": "directory deleted successfully"}), 200

        @self.app.route('/list_directory', methods=['GET'])
        def list_directory():
            #listamos los archivos y directorios dentro de un directorio
            token = request.headers.get('Authorization')
            if token not in self.tokens:
                return jsonify({"message": "unauthorized"}), 401

            path = request.args.get('path')

            if not path:
                return jsonify({"message": "missing directory path"}), 400

            if path not in self.filesystem or self.filesystem[path] != "directory":
                return jsonify({"message": "directory not found"}), 404

            contents = [key for key in self.filesystem.keys() if key.startswith(path)]
            return jsonify({"contents": contents}), 200

        @self.app.route('/get_block_locations', methods=['GET'])
        def get_block_locations():
            #obtenemos las ubicaciones de los bloques de un archivo
            token = request.headers.get('Authorization')
            if token not in self.tokens:
                return jsonify({"message": "unauthorized"}), 401

            path = request.args.get('path')

            if not path:
                return jsonify({"message": "missing file path"}), 400

            if path not in self.block_locations:
                return jsonify({"message": "file not found"}), 404

            blocks = self.block_locations[path]
            return jsonify({
                "blocks_quantity": len(blocks),
                "blocks": [
                    {
                        "block_index": block['block_index'],
                        "block_id": block['block_id'],
                        "datanodes": block.get("datanodes", [])  #así aseguramos que siempre haya una lista de datanodes, aún cuando nadie lo tenga (eso sería raro XD)
                    } for block in blocks
                ]
            }), 200


        @self.app.route('/register_datanode', methods=['POST'])
        def register_datanode():
            #registramos un nuevo DataNode en el sistema
            data = request.json
            datanode_ip = data.get('datanode_ip')
            datanode_port = data.get('datanode_port')

            if not datanode_ip or not datanode_port:
                return jsonify({"message": "missing DataNode IP or port"}), 400

            self.datanodes[f"{datanode_ip}:{datanode_port}"] = {
                "ip": datanode_ip,
                "port": datanode_port
            }

            return jsonify({
                "message": "DataNode registered successfully",
                "block_size": self.block_size,
                "heartbeat_interval": self.heartbeat_interval,
                "block_report_interval": self.block_check_interval
            }), 200
        
        @self.app.route('/heartbeat', methods=['POST'])
        def heartbeat():
            #recibimos el heartbeat de un DataNode
            data = request.json
            datanode_ip = data.get('datanode_ip')
            datanode_port = data.get('datanode_port')

            if not datanode_ip or not datanode_port:
                return jsonify({"message": "missing DataNode IP or port"}), 400

            datanode_key = f"{datanode_ip}:{datanode_port}"
            if datanode_key not in self.datanodes:
                return jsonify({"message": "DataNode not registered"}), 404

            return jsonify({"message": "heartbeat received"}), 200
        
        @self.app.route('/block_report', methods=['POST'])
        def block_report():
            #recibimos un reporte de bloques de un DataNode
            data = request.json
            datanode_ip = data.get('datanode_ip')
            datanode_port = data.get('datanode_port')
            blocks = data.get('blocks', [])  #Esto garantiza que tengamos al menos una lista vacía

            #verificación de los campos obligatorios
            if not datanode_ip or not datanode_port:
                return jsonify({"message": "missing DataNode IP or port"}), 400

            datanode_key = f"{datanode_ip}:{datanode_port}"
            if datanode_key not in self.datanodes:
                return jsonify({"message": "DataNode not registered"}), 404

            #si no hay bloques reportados, retornamos un mensaje indicando que el reporte está vacío
            if not blocks:
                return jsonify({"message": "block report is empty"}), 200

            #procesamos los bloques enviados, si es que hay alguno
            for block in blocks:
                block_id = block.get('block_id')
                checksum = block.get('checksum')

                #validamos que se hayan enviado correctamente los datos del bloque
                if not block_id or not checksum:
                    continue

                #verificamos si el bloque ya existe en las ubicaciones
                block_found = False
                for path, block_list in self.block_locations.items():
                    for stored_block in block_list:
                        if stored_block['block_id'] == block_id:
                            #Si el bloque ya tiene ubicaciones, agregamos el DataNode sin reemplazar las anteriores
                            if "datanodes" not in stored_block:
                                stored_block['datanodes'] = []
                            stored_block['datanodes'].append({
                                "ip": datanode_ip,
                                "port": datanode_port,
                                "checksum": checksum
                            })
                            block_found = True
                            break

            #si no hay bloques, el ciclo for simplemente no hará nada, lo cual es correcto.
            return jsonify({"message": "block report received"}), 200


    def start_server(self):
        #iniciamos el servidor API REST con Flask
        self.app.run(host=self.own_ip, port=self.own_port, debug=True)
