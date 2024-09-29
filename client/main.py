import json
import sys
import os
from CN import Client

class FileSystemClientApp:
    def __init__(self):
        self.client = None
        #el bootstrap tiene información como la dirección IP y el puerto propios del NameNode
        self.bootstrap_path = os.path.join(os.path.dirname(__file__), 'bootstrap.json')
        self.load_bootstrap()

    def load_bootstrap(self):
        try:
            #cargamos la configuración del NameNode desde el archivo bootstrap.json
            with open(self.bootstrap_path, 'r') as file:
                config = json.load(file)
                namenode_ip = config.get('namenode_ip')
                namenode_port = config.get('namenode_port')

                if not namenode_ip or not namenode_port:
                    raise ValueError("Invalid bootstrap.json. 'namenode_ip' or 'namenode_port' missing.")

                #inicializamos el cliente con la configuración del NameNode cargada
                self.client = Client(namenode_ip, namenode_port)
                print(f"Client initialized with NameNode {namenode_ip}:{namenode_port}")
        except Exception as e:
            print(f"Failed to load bootstrap.json: {e}")
            sys.exit(1)

    def start(self):
        while True:
            try:
                command = input(f'{self.client.current_directory}$ ').strip().split()
                if len(command) == 0:
                    continue

                action = command[0]

                if action == 'register':
                    if len(command) != 3:
                        print('Usage: register <username> <password>')
                    else:
                        self.client.register(command[1], command[2])

                elif action == 'login':
                    if len(command) != 3:
                        print('Usage: login <username> <password>')
                    else:
                        self.client.login(command[1], command[2])

                elif action == 'logout':
                    self.client.logout()

                elif action == 'put':
                    if len(command) != 2:
                        print('Usage: put <file_path>')
                    else:
                        file_path = command[1]
                        try:
                            with open(file_path, 'rb') as file:
                                file_data = file.read()
                                self.client.create_file(file_path, file_data)
                        except FileNotFoundError:
                            print(f'File not found: {file_path}')
                
                elif action == 'get':
                    if len(command) != 2:
                        print('Usage: get <remote_file_path>')
                    else:
                        remote_file_path = command[1]
                        self.client.read_file(remote_file_path)

                elif action == 'rm':
                    if len(command) != 2:
                        print('Usage: rm <file_path>')
                    else:
                        self.client.delete_file(command[1])

                elif action == 'mkdir':
                    if len(command) != 2:
                        print('Usage: mkdir <directory_path>')
                    else:
                        self.client.create_directory(command[1])

                elif action == 'rmdir':
                    if len(command) != 2:
                        print('Usage: rmdir <directory_path>')
                    else:
                        self.client.delete_directory(command[1])

                elif action == 'ls':
                    if len(command) != 2:
                        print('Usage: ls <directory_path>')
                    else:
                        self.client.list_directory(command[1])

                elif action == 'cd':
                    if len(command) != 2:
                        print('Usage: cd <directory_path>')
                    else:
                        self.client.change_directory(command[1])

                elif action == 'help':
                    print('','='*20,
                          'COMMANDS:',
                          'register <username> <password>',
                          'login <username> <password>',
                          'logout',
                          'put <file_path>',
                          'get <remote_file_path>',
                          'rm <file_path>',
                          'mkdir <directory_path>',
                          'rmdir <directory_path>',
                          'ls <directory_path>',
                          'cd <directory_path>',
                          'help',
                          'exit',
                          '='*20,
                          sep='\n| ')

                elif action == 'exit':
                    print('Exiting...')
                    sys.exit(0)

                else:
                    print(f'Unknown command: {action}')
            except KeyboardInterrupt:
                print('Exiting...')
                sys.exit(0)

if __name__ == "__main__":
    app = FileSystemClientApp()
    app.start()
