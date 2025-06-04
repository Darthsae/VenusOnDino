import pygame, numpy, socket, select, json

from common import BUFFER_SIZE, PORT, SERVER_IP, Map, Entity

def client():
    with open("map.json") as map_file:
        map_data = json.load(map_file)
        map: Map = Map(map_data)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_socket.sendto("JOIN".encode(), (SERVER_IP, PORT))
    data, addr = client_socket.recvfrom(BUFFER_SIZE)
    player_id = data.decode()
    print(player_id)

    while True:
        client_socket.sendto(f"{player_id}".encode(), (SERVER_IP, PORT))
        data, addr = client_socket.recvfrom(BUFFER_SIZE)
        print(f"{data} - {addr}")

client()