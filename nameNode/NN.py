import json
from flask import Flask, request, jsonify

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
        self.datanodes = {}  #diccionario para los DataNodes registrados

        #inicializamos las rutas del API REST
        self.define_routes()

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

            token = "jwt_token"
            return jsonify({"message": "login successful", "token": token, "block_size": self.block_size}), 200

        @self.app.route('/create_file', methods=['POST'])
        def create_file():
            #creamos un archivo nuevo en el sistema
            token = request.headers.get('Authorization')
            if token != "Bearer jwt_token":
                return jsonify({"message": "unauthorized"}), 401

            data = request.json
            path = data.get('path')

            if not path:
                return jsonify({"message": "missing file path"}), 400

            if path in self.filesystem:
                return jsonify({"message": "file already exists"}), 400

            #simulamos la asignación de bloques a DataNodes
            blocks = [
                {"block_id": "block1", "datanode": {"ip": "172.31.93.40", "port": 5001}},
                {"block_id": "block2", "datanode": {"ip": "172.31.93.41", "port": 5001}}
            ]
            self.filesystem[path] = blocks
            self.block_locations[path] = blocks

            return jsonify({"blocks": blocks}), 200

        @self.app.route('/delete_file', methods=['DELETE'])
        def delete_file():
            #eliminamos un archivo del sistema
            token = request.headers.get('Authorization')
            if token != "Bearer jwt_token":
                return jsonify({"message": "unauthorized"}), 401

            path = request.args.get('path')

            if not path:
                return jsonify({"message": "missing file path"}), 400

            if path not in self.filesystem:
                return jsonify({"message": "file not found"}), 404

            del self.filesystem[path]
            del self.block_locations[path]

            return jsonify({"message": "file deleted successfully"}), 200

        @self.app.route('/create_directory', methods=['POST'])
        def create_directory():
            #creamos un directorio nuevo en el sistema
            token = request.headers.get('Authorization')
            if token != "Bearer jwt_token":
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
            if token != "Bearer jwt_token":
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
            if token != "Bearer jwt_token":
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
            if token != "Bearer jwt_token":
                return jsonify({"message": "unauthorized"}), 401

            path = request.args.get('path')

            if not path:
                return jsonify({"message": "missing file path"}), 400

            if path not in self.block_locations:
                return jsonify({"message": "file not found"}), 404

            blocks = self.block_locations[path]
            return jsonify({"blocks": blocks}), 200

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

    def start_server(self):
        #iniciamos el servidor API REST con Flask
        self.app.run(host=self.own_ip, port=self.own_port, debug=True)
