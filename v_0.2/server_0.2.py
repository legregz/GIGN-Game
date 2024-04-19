import socket, json, time, random, os
from threading import Thread

SERVER_HOST = "localhost"
SERVER_PORT = 55352

clientSockets = []
games = []
serverSocket = socket.socket()
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((SERVER_HOST, SERVER_PORT))
serverSocket.listen(10)

startTime = time.time()

class Log:
    def __init__(self):
        pass

    def log(self, log):
        file = open("log.txt", "a")
        file.write(f"{int((time.time() - startTime) * 1000)}: {log}\n")
        print(f"{int((time.time() - startTime) * 1000)}: {log}")
        file.close()

log = Log()
log.log(f"server launched")

def separate(msg):
    msgs = []
    start = 0
    for i in range(len(msg)):
        if msg[i] == ")":
            msgs.append(msg[start:i + 1])
            start = i + 1
    return msgs

class Game:
    def __init__(self):
        games.append(self)
        self.index = len(games) - 1
        founded = True
        self.code = ""
        while founded == True:
            founded = True
            for i in range(6):
                self.code += str(random.randint(0, 9))
            for game in games:
                if game.code == self.code:
                    founded = False

        self.players = [[], []]

    def connect(self, player):
        self.brodcast(f"newPlayer('{player.userData['username']}')")
        for elt in self.players:
            player.send(f"newPlayer('{elt.userData['username']}')")

        self.players[0].append(player)
        return self
    
    def changeTeam(self, player):
        index = None
        for i in range(len(self.players)):
            for j in range(len(self.players[i])):
                if self.players[i][j] == player:
                    self.players[i].pop[j]
                    index = i
                    break

            if index != None:
                break


        if index == len(self.players) - 1:
            self.players[0].append(player)
        else:
            self.players[index + 1].append(player)

        print(self.players)
        self.brodcast(f"changeTeam('{player.userData['username']}')")

    def launchGame(self, player):
        self.brodcast("gameStarted()")

    def brodcast(self, msg):
        for i in range(2):
            for player in self.players[i]:
                player.send(msg)

class Client:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address

        self.listener = Thread(target = self.listen, args = ())
        self.listener.daemon = True
        self.listener.start()

    def listen(self):
        while True:
            try:
                msgs = separate(self.socket.recv(2048).decode())
            except Exception as e:
                log.log(f"[!] Error: {e}")
                self.socket.close()
                return 1
            else:
                for msg in msgs:
                    try:
                        eval("self." + msg)
                    except Exception as e:
                        log.log(f"[!] Error: {e} : Unknown command: {msg}")

    def send(self, msg):
        self.socket.send(bytes(msg, "utf-8"))

    def login(self, username, password):
        users = os.listdir("users")

        founded = False
        for user in range(len(users)):
            if users[user][0:-5] == username:
                founded = True

                file = open(f"users/{username}", "r")
                userData = eval(file.read())
                file.close()

                if userData["password"] == password:
                    self.userData = userData
                    self.send(f"login(True, {self.userData})")
                    log.log(f"player {self.userData['username']} is logged in")
                else:
                    self.send(f"login(False, '0001')")
                    log.log(f"player {users[user][0:-5]} try to login")
                break

        if founded == False:
            self.send(f"login(False, '0001')")
            log.log(f"{self.address[0]} try to login")

    def signin(self, username, password, confirmation):
        users = os.listdir("users")

        founded = False
        for user in range(len(users)):
            if users[user] == username:
                founded = True
                break

        if founded == False:
            if len(username) > 2:
                if password == confirmation:
                    if len(password) > 7:
                        userData = {'username':username, "password":password}
                        file = open(f"users/{username}.json", "w")
                        file.write(json.dumps(userData))
                        file.close()

                        self.userData = userData
                        self.send(f"login(True, {self.userData})")
                        log.log(f"player {self.userData['username']} have create account")
                    else:
                        self.send(f"login(False, '0002')")
                        log.log(f"{self.address[0]} try to create account")
                else:
                    self.send(f"login(False, '0003')")
                    log.log(f"{self.address[0]} try to create account")
            else:
                self.send(f"login(False, '0004')")
                log.log(f"{self.address[0]} try to create account")
        else:
            self.send(f"login(False, '0005')")
            log.log(f"{self.address[0]} try to create account")

    def createGame(self):
        game = Game()
        self.game = game.connect(self)
        print(self.game.code)
        self.send(f"connectedToGame(True, {self.game.code})")
        log.log(f"player {self.userData['username']} create a game")

    def changeTeam(self):
        self.game.changeTeam(self)

    def startGame(self):
        self.game.launchGame(self)

    def connectToGame(self, code):
        founded = False
        for i in range(len(games)):
            if games[i].code == code:
                founded = True
                self.game = games[i].connect(self)
                self.send(f"connectedToGame(True, {self.game.code})")
                log.log(f"player {self.userData['username']} connect himself to a game")
                break
        
        if founded == False:
            self.send(f"connectedToGame(True, '0020')")
            log.log(f"player {self.userData['username']} try to connect himself to a game")

    def escape(self):
        log.log(f"{self.address[0]} quit the game")
        self.socket.close()
        return 0

while True:
    clientSocket, clientAddress = serverSocket.accept()
    log.log(f"{clientAddress[0]} is connected")
    try:
        clientSockets.append(Client(clientSocket, clientAddress))
    except Exception as e:
        log.log(e)