#!/bin/bash

echo "Selecciona el tipo de nodo:"
echo "1. client (Python)"
echo "2. nameNode (Python)"
echo "3. dataNode (Go)"
read -p "Ingresa el número, inicial o tipo de tu selección: " selection
selection=$(echo "$selection" | tr '[:upper:]' '[:lower:]')

if [[ "$selection" == "1" || "$selection" == "c" || "$selection" == "client" ]]; then
    cd client
    echo "Entraste en el directorio 'client'"
    git pull
    python3 main.py

elif [[ "$selection" == "2" || "$selection" == "n" || "$selection" == "namenode" ]]; then
    cd nameNode
    echo "Entraste en el directorio 'nameNode'"
    git pull
    python3 main.py

elif [[ "$selection" == "3" || "$selection" == "d" || "$selection" == "datanode" ]]; then
    cd dataNode
    echo "Entraste en el directorio 'dataNode'"
    git pull
    go build main.go
    ./main

else
    echo "Selección inválida"
    exit 1
fi
