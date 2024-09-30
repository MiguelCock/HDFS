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
        self.heartbeat_interval = config['heartbeat_interval']  #intervalo de heartbeat
        self.block_check_interval = config['block_check_interval']  #intervalo de verificación de bloques
        self.replication_check_interval = config['replication_check_interval']  #verificación de replicación

        self.filesystem = {}       #diccionario para gestionar archivos y directorios
        self.block_locations = {}  #diccionario para rastrear la ubicación de bloques
        self.file_owners = {}      #diccionario para rastrear el dueño de cada archivo
        self.clients = {}          #diccionario para los clientes registrados
        self.tokens = {}           #diccionario para los tokens de los clientes
        self.datanodes = {}        #diccionario para los DataNodes registrados (con TTL)

        #inicializamos las rutas del API REST
        self.define_routes()

        #iniciamos los hilos para manejar TTL y replicación
        threading.Thread(target=self.decrease_ttl, daemon=True).start()
        threading.Thread(target=self.check_block_replication, daemon=True).start()

    def generate_user_token(self, username, password):
        #generamos un token para el usuario
        text_to_hash = f"{username}|{password}"
        hash_object = hashlib.md5(text_to_hash.encode())
        return hash_object.hexdigest()[:16]

    def generate_block_id(self, file_path, part_number):
        #generamos un ID único para cada bloque
        text_to_hash = f"{file_path}.part{part_number}"
        hash_object = hashlib.md5(text_to_hash.encode())
        return hash_object.hexdigest()[:16]

    def decrease_ttl(self):
        #cada 10 segundos, decrementamos el TTL de los DataNodes y eliminamos los que expiren
        while True:
            time.sleep(10)
            for datanode_key, info in list(self.datanodes.items()):
                info["TTL"] -= 1
                if info["TTL"] <= 0:
                    print(f"DataNode {datanode_key} removed due to TTL expiration.")
                    #eliminamos el DataNode de los registros y de los bloques
                    del self.datanodes[datanode_key]
                    self.remove_datanode_from_blocks(datanode_key)

    def remove_datanode_from_blocks(self, datanode_key):
        #elimina un DataNode de todos los bloques en block_locations
        for path, blocks in self.block_locations.items():
            for block in blocks:
                block['datanodes'] = [dn for dn in block['datanodes'] if f"{dn['ip']}:{dn['port']}" != datanode_key]

    def check_block_replication(self):
        #verificamos que cada bloque tenga al menos dos réplicas
        while True:
            time.sleep(self.replication_check_interval)
            print("Checking block replication status...")

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

        #filtramos los DataNodes que ya tienen el bloque
        filtered_datanodes_with_block = [{'ip': dn['ip'], 'port': dn['port']} for dn in datanodes_with_block]

        #elegimos un DataNode aleatorio que NO tenga este bloque
        available_datanodes = [node for node in self.datanodes.values() if {'ip': node['ip'], 'port': node['port']} not in filtered_datanodes_with_block]
        if not available_datanodes:
            print("No available DataNodes for replication.")
            return

        target_datanode = random.choice(available_datanodes)

        #hacemos la petición para replicar el bloque en otro DataNode
        url = f"http://{source_datanode['ip']}:{source_datanode['port']}/replicate_block"
        params = {
            'block_id': block_id,
            'target_datanode_ip': target_datanode['ip'],
            'target_datanode_port': target_datanode['port'] + 1
        }

        print(f"Replicating block {block_id} from {source_datanode['ip']}:{source_datanode['port']} to {target_datanode['ip']}:{target_datanode['port'] + 1}...")

        try:
            response = requests.post(url, params=params)
            response_message = response.json().get('message', 'No message')
            if response.status_code == 200:
                print(f"Block {block_id} successfully replicated. {response_message}")
                #actualizamos las ubicaciones de los bloques sin duplicar
                if not any(dn['ip'] == target_datanode['ip'] and dn['port'] == target_datanode['port'] for dn in block['datanodes']):
                    block['datanodes'].append({
                        "ip": target_datanode['ip'],
                        "port": target_datanode['port'],
                        "TTL": 2
                    })
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

            owner = self.tokens[token]  #obtenemos el dueño del archivo

            #calculamos la cantidad de bloques
            blocks_quantity = (size // self.block_size) + (1 if size % self.block_size != 0 else 0)
            blocks = []

            for i in range(blocks_quantity):
                #seleccionamos un DataNode aleatoriamente
                selected_datanode = random.choice(list(self.datanodes.values()))

                #generamos el block_id
                block_id = self.generate_block_id(path, i + 1)

                block = {
                    "block_index": i + 1,
                    "block_id": block_id,
                    "datanodes": [{
                        "ip": selected_datanode['ip'],
                        "port": selected_datanode['port'],
                        "TTL": 2
                    }]
                }
                blocks.append(block)

            #almacenamos la información del archivo
            self.filesystem[path] = blocks
            self.file_owners[path] = owner
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

            owner = self.file_owners.get(path)
            if owner != self.tokens[token]:
                return jsonify({"message": "forbidden, only the owner can delete this file"}), 403

            #obtenemos la lista de bloques del archivo
            blocks = self.filesystem[path]

            #para cada bloque, contactamos a cada DataNode y le pedimos que elimine el bloque
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

            #eliminamos el archivo del sistema
            del self.filesystem[path]
            del self.block_locations[path]
            del self.file_owners[path]

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

            owner = self.file_owners.get(path)
            if owner != self.tokens[token]:
                return jsonify({"message": "forbidden, only the owner can access this file"}), 403

            blocks = self.block_locations[path]
            return jsonify({
                "blocks_quantity": len(blocks),
                "blocks": [
                    {
                        "block_index": block['block_index'],
                        "block_id": block['block_id'],
                        "datanodes": block.get("datanodes", [])
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

            datanode_key = f"{datanode_ip}:{datanode_port}"
            self.datanodes[datanode_key] = {
                "ip": datanode_ip,
                "port": datanode_port,
                "TTL": 2
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

            #restablecemos el TTL a 2 cuando recibimos un heartbeat
            self.datanodes[datanode_key]["TTL"] = 2
            return jsonify({"message": "heartbeat received"}), 200

        @self.app.route('/block_report', methods=['POST'])
        def block_report():
            #recibimos un reporte de bloques de un DataNode
            data = request.json
            datanode_ip = data.get('datanode_ip')
            datanode_port = data.get('datanode_port')
            blocks = data.get('blocks', [])

            #verificación de los campos obligatorios
            if not datanode_ip or not datanode_port:
                return jsonify({"message": "missing DataNode IP or port"}), 400

            datanode_key = f"{datanode_ip}:{datanode_port}"
            if datanode_key not in self.datanodes:
                return jsonify({"message": "DataNode not registered"}), 404

            #actualizamos el TTL del DataNode
            self.datanodes[datanode_key]["TTL"] = 2

            #si el reporte no contiene bloques, devolvemos una respuesta adecuada
            if not blocks:
                print(f"No blocks reported by DataNode {datanode_key}.")
                return jsonify({"message": "No blocks to report"}), 200

            #obtener los IDs de bloques reportados
            reported_block_ids = [block.get('block_id') for block in blocks]

            #validamos cada bloque registrado en el NameNode
            for path, block_list in self.block_locations.items():
                for stored_block in block_list:
                    block_id = stored_block['block_id']
                    #si el DataNode no reporta un bloque que antes tenía, lo eliminamos de 'datanodes'
                    if not any(bid == block_id for bid in reported_block_ids):
                        stored_block['datanodes'] = [dn for dn in stored_block['datanodes'] if f"{dn['ip']}:{dn['port']}" != datanode_key]
                    #else:
                    #    #si el checksum no coincide, eliminamos el bloque del DataNode
                    #    reported_block = next((b for b in blocks if b['block_id'] == block_id), None)
                    #    if reported_block and reported_block['checksum'] != stored_block.get('checksum'):
                    #        print(f"Checksum mismatch for block {block_id} on DataNode {datanode_key}. Removing corrupt block.")
                    #        self.delete_block_on_datanode(datanode_ip, datanode_port, block_id)
                    #        stored_block['datanodes'] = [dn for dn in stored_block['datanodes'] if f"{dn['ip']}:{dn['port']}" != datanode_key]

            #procesamos los bloques nuevos o actualizados en el 'block_report'
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
                            block_found = True
                            #verificamos que no se duplique el DataNode en los bloques
                            if not any(dn['ip'] == datanode_ip and dn['port'] == datanode_port for dn in stored_block['datanodes']):
                                stored_block['datanodes'].append({
                                    "ip": datanode_ip,
                                    "port": datanode_port,
                                    "TTL": 2,
                                    "checksum": checksum
                                })
                #si no se encontró el bloque, podría ser uno nuevo (caso especial)
                if not block_found:
                    print(f"Unknown block {block_id} reported by DataNode {datanode_key}. Ignoring.")

            #si no hay bloques, el ciclo for simplemente no hará nada, lo cual es correcto.
            return jsonify({"message": "block report received"}), 200

    def delete_block_on_datanode(self, datanode_ip, datanode_port, block_id):
        #solicitamos al DataNode que elimine el bloque corrupto
        url = f"http://{datanode_ip}:{datanode_port}/delete_block"
        try:
            response = requests.delete(url, params={"block_id": block_id})
            if response.status_code == 200:
                print(f"Block {block_id} deleted from DataNode {datanode_ip}:{datanode_port}")
            else:
                print(f"Failed to delete block {block_id} from DataNode {datanode_ip}:{datanode_port}")
        except Exception as e:
            print(f"Error contacting DataNode {datanode_ip}:{datanode_port}: {e}")

    def start_server(self):
        #iniciamos el servidor API REST con Flask
        self.app.run(host=self.own_ip, port=self.own_port)
