import socket, json
from threading import Thread

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 55352

clientSockets = []
serverSocket = socket.socket()
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((SERVER_HOST, SERVER_PORT))
serverSocket.listen(10)

def separate(msg):
    msgs = []
    start = 0
    for i in range(len(msg) - 2):
        if msg[i:i + 2] == "][":
            msgs.append(msg[start:i + 1])
            start = i + 1
        elif i == len(msg) - 3:
            msgs.append(msg[start:i + 3])
            start = i + 1
    return msgs

class Client:
    def __init__(self, socket):
        self.socket = socket
        file = open("data.json")
        self.userData = eval(file.read())
        file.close()

        self.listener = Thread(target = self.listen, args = ())
        self.listener.daemon = True
        self.listener.start()

    def listen(self):
        while True:
            try:
                msgs = separate(self.socket.recv(2048).decode())
            except Exception as e:
                print(f"[!] Error: {e}")
                self.socket.close()
                return 1
            else:
                for msg in msgs:
                    if msg[0] == "[" and msg[-1] == "]":
                        evaluateMsg = eval(msg)

                        args = "("
                        for i in range(1, len(evaluateMsg)):
                            args += f"'{evaluateMsg[i]}',"
                        args += ")"
                            
                        try:
                            eval(f"self.{evaluateMsg[0]}{args}")
                        except Exception as e:
                            print(f"[!] Error: {e} : Unknown command")

    def login(self, username, password):
        founded = False
        for player in range(len(self.userData)):
            if self.userData[player]["username"] == username:
                founded = True

                if self.userData[player]["password"] == password:
                    self.userData = self.userData[player]
                    self.send(["login", True, self.userData])
                else:
                    self.send(["login", False, "Le nom d'utilisateur ou le mot de passe sont incorrects"])
                break

        if founded == False:
            self.send(["login", False, "Le nom d'utilisateur ou le mot de passe sont incorrects"])

    def signin(self, username, password, confirmation):
        founded = False
        for key in list(self.userData.keys()):
            if self.userData[key]["username"] == username:
                founded = True
                break

        if founded == False:
            if len(username) > 2:
                if password == confirmation:
                    if len(password) > 7:
                        self.userData.append({"username":username, "password":password, "invitations":[]})
                        saved = False
                        while saved == False:
                            try:
                                file = open("data.json", "w")
                                file.write(json.dumps(self.userData))
                                file.close()
                                saved = True
                            except:
                                pass
                        self.userData = self.userData[key]
                        self.send(["signin", True, self.userData])
                    else:
                        self.send(["signin", False, "Le mot de passe doit faire au moins 8 caractères"])
                else:
                    self.send(["signin", False, "Les deux mots de passe doivent correspondre"])
            else:
                self.send(["signin", False, "Le nom d'utilisateur doit faire au moins 3 caractères"])
        else:
            self.send(["signin", False, "Le nom d'utilisateur est deja pris"])

    def invite(self, playerName):
        for client in clientSockets:
            try:
                if client.userData["username"] == playerName:
                    client.invitedBy(self.userData["username"])
            except:
                pass

        file = open("data.json")
        data = eval(file.read())
        file.close()

        for key in list(data.keys()):
            if data[key]["username"] == playerName:
                data[key]["invitations"].append(playerName)

        saved = False
        while saved == False:
            try:
                file = open("data.json", "w")
                file.write(json.dumps(data))
                file.close()
                saved = True
            except:
                pass

    def invitedBy(self, playerName):
        self.send(["invited", playerName])

    def send(self, msg):
        self.socket.send(bytes(str(msg), "utf-8"))

while True:
    clientSocket, clientAddress = serverSocket.accept()
    print(f"{clientAddress[0]} is connected")
    clientSockets.append(Client(clientSocket))

for client in clientSockets:
    client.socket.close()
serverSocket.close()