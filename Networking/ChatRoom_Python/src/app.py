import pygame, socket, asyncio, threading
from pygame_gui.elements import UIPanel, UIButton, UITextEntryLine, UITextBox
from enum import Enum
from threading import Thread

class Screen(Enum):
    MAIN_MENU = 0
    CHAT_CLIENT = 1

class Application:
    def __init__(self):
        self.screen = Screen.MAIN_MENU
        self.host = False
        self.running = True

    def run(self):
        while self.running:
            match self.screen:
                case Screen.MAIN_MENU:
                    ...
                case Screen.CHAT_CLIENT:
                    if self.host:
                        ...
                    else:
                        ...
    
    def hostNew(self):
        self.screen = Screen.CHAT_CLIENT
        self.host = True
        self.clients = []
        self.host_thread: Thread = Thread(target=self.host_function)
        self.host_thread.start()
    
    def joinClient(self):
        self.screen = Screen.CHAT_CLIENT
        self.host = False

    def close(self):
        if self.host:
            self.host_thread.join()
    
    def host_function(self):
        with socket.create_server(("", 8000)) as server:
            while True:
                conn, addr = server.accept()
                self.clients.append((conn, addr))