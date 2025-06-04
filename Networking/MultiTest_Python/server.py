import pygame, numpy, socket, uuid, json

from common import BUFFER_SIZE, PORT, SERVER_IP, Map, Entity

def server():
    with open("map.json") as map_file:
        map_data = json.load(map_file)
        map: Map = Map(map_data)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, PORT))

    players: dict[uuid.UUID, Entity] = {}

    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        info = data.decode()
        print(f"{info}")
        match info[:4]:
            case "JOIN":
                player_uuid: uuid.UUID = uuid.uuid4()
                players[player_uuid] = Entity(12, 12)
                server_socket.sendto(f"{player_uuid}|{players[player_uuid]}".encode(), addr)

server()