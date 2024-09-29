import json
from flask import Flask, request, jsonify
import hashlib
import random
import requests
import threading
import time

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
        self.replication_check_interval = config['replication_check_interval']  #intervalo para la verificación de replicación


        self.filesystem = {}  #diccionario para gestionar archivos y directorios
        self.block_locations = {}  #diccionario para rastrear la ubicación de bloques
        self.clients = {}  #diccionario para los clientes registrados
        self.tokens = {}  #diccionario para los tokens de los clientes logeados en el sistema
        self.datanodes = {}  #diccionario para los DataNodes registrados

        #inicializamos las rutas del API REST
        self.define_routes()

        #iniciamos el proceso de verificación de mínima replicación (dos DataNodes por bloque)
        threading.Thread(target=self.check_block_replication, daemon=True).start()

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

    def check_block_replication(self):
        #este hilo se ejecuta periódicamente y revisa que cada bloque tenga al menos dos réplicas
        while True:
            time.sleep(self.replication_check_interval)  #esperamos el tiempo puesto en el bootstrap
            print("Checking block replication status...")

            #DEBUG
            print('block_locations:', self.block_locations)
            #END DEBUG

            for path, blocks in self.block_locations.items():
                for block in blocks:
                    if len(block.get('datanodes', [])) < 2:
                        print(f"Block {block['block_id']} needs replication.")
                        self.replicate_block(block)

    def replicate_block(self, block):
        #lógica para replicar un bloque si no tiene suficientes réplicas
        datanodes_with_block = block.get('datanodes', [])
        if not datanodes_with_block:
            print(f"No DataNode found for block {block['block_id']}")
            return
        
        #seleccionamos un DataNode que tenga el bloque
        source_datanode = random.choice(datanodes_with_block)
        block_id = block['block_id']

        #quitando el atributo checksum y otros posibles que vengan en el futuro
        filtered_datanodes_with_block = [{'ip':datanode['ip'], 'port':datanode['port']} for datanode in datanodes_with_block]

        #elegimos un DataNode aleatorio que NO tenga este bloque
        available_datanodes = [
            node for node in self.datanodes.values()
            if node not in filtered_datanodes_with_block
        ]

        if not available_datanodes:
            print("No available DataNodes for replication.")
            return

        target_datanode = random.choice(available_datanodes)

        #hacemos la petición para replicar el bloque en otro DataNode
        url = f"http://{source_datanode['ip']}:{source_datanode['port']}/replicate_block"
        params = {
            'block_id': block_id,
            'target_datanode_ip': target_datanode['ip'],
            'target_datanode_port': target_datanode['port']+1
        }

        print(f"Replicating block {block_id} from {source_datanode['ip']}:{source_datanode['port']} to {target_datanode['ip']}:{target_datanode['port']+1}...")

        # DEBUG
        print('datanodes_with_block:', datanodes_with_block)
        print('self.datanodes:', self.datanodes)
        print('available_datanodes:', available_datanodes)
        # END DEBUG

        try:
            response = requests.post(url, params=params)
            response_message = response.json().get('message', 'No message')
            if response.status_code == 200:
                print(f"Block {block_id} successfully replicated from {source_datanode['ip']} to {target_datanode['ip']}. {response_message}")
                #actualizamos las ubicaciones de los bloques
                block['datanodes'].append(target_datanode)
            else:
                print(f"Failed to replicate block {block_id}. {response_message}")
        except Exception as e:
            print(f"Error during replication: {e}")
    
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
        self.app.run(host=self.own_ip, port=self.own_port)
