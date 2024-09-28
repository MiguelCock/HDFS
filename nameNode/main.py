from NN import NameNode

#ruta del archivo bootstrap.json
bootstrap_path = './bootstrap.json'

def main():
    #creamos instancia del NameNode con los valores del archivo bootstrap.json
    nn = NameNode(bootstrap_path)
    #iniciamos el servidor REST
    nn.start_server()

if __name__ == "__main__":
    main()
