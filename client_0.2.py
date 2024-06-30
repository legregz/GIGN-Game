import socket, pygame, select, time
from threading import Thread

SERVER_HOST = "localhost"
SERVER_PORT = 55352

online = False
menu = "homeMenu()"
players = {}
errorCode = ""
lang = "en"

def connect():
    global clientSocket, online
    while online != True:
        try:
            clientSocket = socket.socket()
            clientSocket.connect((SERVER_HOST, SERVER_PORT))
            online = True
        except:
            pass
        time.sleep(5)

def send(msg):
    clientSocket.send(bytes(msg, "utf-8"))

def separate(msg):
    msgs = []
    start = 0
    for i in range(len(msg)):
        if msg[i] == ")":
            msgs.append(msg[start:i + 1])
            start = i + 1
    return msgs

def socketListen():
    read_sockets, write_socket, error_socket = select.select([clientSocket],[],[])

    for socks in read_sockets:
        if socks == clientSocket:
            try:
                msgs = separate(socks.recv(2048).decode())
            except:
                print("Connexion failed!")

            return msgs

def startListenner():
    listenner = Thread(target = listen, args = ())
    listenner.daemon = True
    listenner.start()

def listen():
    global run
    while run == True:
        msgs = socketListen()
        for msg in msgs:
            if len(msg) > 0:
                try:
                    eval(msg)
                except Exception as e:
                    print(e)

def escape():
    send("escape()")
    quit()

connecter = Thread(target = connect, args = ())
connecter.daemon = True
connecter.start()

pygame.init()
screen = pygame.display.set_mode()
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
pygame.key.set_repeat(500, 100)

userData = {}

file = open("colors.json", "r")
colorDict = eval(file.read())
file.close()

def createColor(color):
    if type(color) == str():
        return colorDict[color]
    else:
        return color
    
def dark(color):
    if type(color) == str:
        return "dark" + color
    else:
        return (max(0, color[0] - 20), max(0, color[1] - 20), max(0, color[2] - 20))

def createRect(position, size):
    return [int(screen.get_width() / 100 * (position[0] - size[0] / 2)), int(screen.get_height() / 100 * (position[1] - size[1] / 2)), int(screen.get_width() / 100 * size[0]), int(screen.get_height() / 100 * size[1])]

def createPosition(position):
    return [int(screen.get_width() / 100 * position[0]), int(screen.get_height() / 100 * position[1])]

def draw(image, rect, centered = (True, True)):
    pos = image.get_rect()
    pos.center = [rect[0] + rect[2] // 2, rect[1] + rect[3] // 2]
    x, y = rect[0], rect[1]
    if centered[0] == True:
        x = pos[0]
    if centered[1] == True:
        y = pos[1]
    screen.blit(image, (x, y))

class Trad:
    def __init__(self):
        file = open("trad.json", "r")
        self.trads = eval(file.read())
        file.close()

        file = open("lang.json", "r")
        langIndex = eval(file.read())
        file.close()

        self.langIndex = langIndex.index(lang)

    def trad(self, code):
        return self.trads[code][self.langIndex]
    
trad = Trad()

class Rect:
    def __init__(self, position, size, color, width = 0):
        self.color = color
        self.width = width
        self.position = position
        self.size = size

    def setPosition(self, position):
        self.position = position

    def show(self, hover = 0):
        pygame.draw.rect(screen, createColor(self.color), createRect(self.position, [self.size[0] + hover, self.size[1] + hover]), int(screen.get_height() // 100 * (self.width)))

class Text:
    def __init__(self, position, size, text, color, font = "PixelBold.otf"):
        self.color = color
        self.font = pygame.font.Font(f"fonts/{font}", screen.get_height() // 100 * size)
        self.position = position
        self.setText(text)

    def setPosition(self, position):
        self.position = position
        self.rects = [createRect([self.position[0], self.position[1] + i * (1 + self.texts[i].get_height() / screen.get_height() * 100) - (len(self.texts) - 1) * self.texts[i].get_height() / screen.get_height() * 100], [self.texts[i].get_width() / screen.get_width() * 100, self.texts[i].get_height() / screen.get_height() * 100]) for i in range(len(self.texts))]

    def setText(self, text):
        start = 0
        try:
            text = trad.trad(text)
        except:
            pass
        self.texts = []
        for end in range(len(text)):
            if text[end: end+2] == "//":
                self.texts.append(text[start: end])
                start = end + 2

            elif end == len(text) - 1:
                self.texts.append(text[start: end+2])
        self.texts = [self.font.render(txt, False, createColor(self.color)) for txt in self.texts]
        
        try:
            self.setPosition(self.position)
        except:
            pass

    def show(self):
        for i in range(len(self.texts)):
            screen.blit(self.texts[i], self.rects[i])

class Button:
    def __init__(self, position, size, color, text, fontSize, textColor, clicked, notification = 0, active = True):
        self.clicked = clicked
        self.size = size
        try:
            self.setPosition(position)
        except:
            pass
        self.fontSize = fontSize
        self.textColor = textColor
        self.active = active

        self.Rect = Rect(position, size, color)
        self.Text = Text(position, fontSize, text, textColor)
        self.notification = 0
        self.notify(notification)

    def setPosition(self, position):
        self.position = position
        self.rect = createRect(position, self.size)

    def notify(self, notification):
        if notification != 0 and notification != self.notification:
                self.notifyText = Text([self.position[0] + self.size[0] / 2, self.position[1] - self.size[1] / 2], self.fontSize, str(notification), "Green")
                self.notification = notification

    def show(self):
        if self.active == True:
            mousePosition = pygame.mouse.get_pos()
            if self.rect[0] < mousePosition[0] < self.rect[0] + self.rect[2] and self.rect[1] < mousePosition[1] < self.rect[1] + self.rect[3]:
                self.Rect.show(1)
            else:
                self.Rect.show()

            self.Text.show()
            if self.notification != 0:
                self.notifyText.show()

    def click(self):
        if self.active == True:
            mousePosition = pygame.mouse.get_pos()
            if self.rect[0] < mousePosition[0] < self.rect[0] + self.rect[2] and self.rect[1] < mousePosition[1] < self.rect[1] + self.rect[3]:
                return self.clicked
            else:
                return ""
        else:
            return ""
        
    def forceClick(self):
        return self.clicked

class ScrollableList:
    def __init__(self, position, size, components):
        self.position = position
        self.size = size
        self.rect = createRect(position, size)
        self.components = components
        self.height = 0
        height = self.height
        for i in range(len(self.components)):
            self.components[i].setPosition([position[0], position[1] - size[1] // 2 + height + self.components[i].size[1] // 2])
            height += self.components[i].size[1]

    def scroll(self, direction):
        mousePosition = pygame.mouse.get_pos()
        if self.rect[0]  < mousePosition[0] < self.rect[0] + self.rect[2] and self.rect[1] < mousePosition[1] < self.rect[1] + self.rect[3]:
            self.height += direction
            height = self.height
            for i in range(len(self.components)):
                self.components[i].setPosition([self.position[0], self.position[1] - self.size[1] // 2 + height + self.components[i].size[1] // 2])
                height += self.components.size[1]

    def click(self):
        for elt in self.components:
            try:
                elt.click()
            except:
                pass

    def show(self):
        for i in range(len(self.components)):
            if self.position[1] - self.size[1] // 2 < self.components[i].position[1] - self.components[i].size[1] // 2 or self.position[1] + self.size[1] // 2 > self.components[i].position[1] + self.components[i].size[1] // 2:
                self.components[i].show()
        
class Entry:
    def __init__(self, position, size, color, defaultText, fontSize, textColor, text = "", font = "PixelBold.otf"):
        self.rect = createRect(position, size)
        self.font = pygame.font.Font(f"fonts/{font}", screen.get_height() // 100 * fontSize)
        try:
            defaultText = trad.trad(defaultText)
        except:
            pass
        self.defaultText = self.font.render(defaultText, True, textColor)
        self.text = text
        self.active = False
        self.color = color
        self.border = Rect(position, size, "Grey", 0.5)

    def click(self):
        mousePosition = pygame.mouse.get_pos()
        if self.rect[0]  < mousePosition[0] < self.rect[0] + self.rect[2] and self.rect[1] < mousePosition[1] < self.rect[1] + self.rect[3]:
            self.active = True
        else:
            self.active = False
            
    def show(self, char):		
        mousePosition = pygame.mouse.get_pos()

        if self.active == False:
            if self.rect[0] < mousePosition[0] < self.rect[0] + self.rect[2] and self.rect[1] < mousePosition[1] < self.rect[1] + self.rect[3]:
                self.border.color = "Grey"
                hover = 1
            else:
                self.border.color = "darkGrey"
                hover = 0

            if len(self.text) == 0:
                draw(self.defaultText, self.rect)
            else:
                draw(self.font.render(self.text, True, createColor("White")), self.rect)
        else:
            if char == "\b":
                self.text = self.text[:-1]
            else:
                self.text += char

            if self.rect[0] < mousePosition[0] < self.rect[0] + self.rect[2] and self.rect[1] < mousePosition[1] < self.rect[1] + self.rect[3]:
                self.border.color = self.color
                hover = 1
            else:
                self.border.color = dark(self.color)
                hover = 0

            draw(self.font.render(self.text + "|", True, createColor("White")), self.rect)

        self.border.show(hover)

class PopUp:
    def __init__(self, position, size, color, components):
        self.delay = 0
        self.active = False
        self.rect = createRect(position, size)
        self.components = components
        self.components.insert(0, Rect(position, size, color))

    def click(self):
        if self.active == True and time.time() > self.delay:
            mousePosition = pygame.mouse.get_pos()
            if self.rect[0]  < mousePosition[0] < self.rect[0] + self.rect[2] and self.rect[1] < mousePosition[1] < self.rect[1] + self.rect[3]:
                pass
            else:
                self.close()
            for elt in self.components:
                try:
                    data = elt.click()
                    if len(data) != 0:
                        return data
                except:
                    pass
            return ""
        else:
            return ""
        
    def show(self, char = ""):
        if self.active == True:
            for elt in self.components:
                try:
                    elt.show(char)
                except:
                    elt.show()

    def open(self):
        self.active = True
        self.delay = time.time() + 0.2

    def close(self):
        self.active = False

def goHomeMenu():
    global menu
    menu = "homeMenu()"

def homeMenu():
    buttons = [
        Button([50, 40], [20, 5], (13, 164, 31), "0013", 4, "White", "goLoginMenu()"),
        Button([50, 60], [20, 5], (13, 164, 31), "0014", 4, "White", "goSigninMenu()")
    ]

    texts = [
        Text([50, 20], 8, "0019", "lightBlue"),
        Text([50, 50], 5, "0017", "Orange"),
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "0008", "White"),
            Button([60, 55], [10, 5], "Red", "0009", 4, "White", "escape()"),
            Button([40, 55], [10, 5], "Green", "0010", 4, "White", "popups[0].close()")
        ]),
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                popups[0].open()

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()

                    if len(data) != 0:
                        evaluateData = eval(data)

                for popup in popups:
                    data = popup.click()
                    
                    if len(data) != 0:
                        eval(data)

        screen.fill(0)

        if online == False:
            texts[1].show()
            for i in range(2):
                buttons[i].active = False
        else:
            for i in range(2):
                buttons[i].active = True

        for button in buttons:
            button.show()

        texts[0].show()

        for popup in popups:
            popup.show()
            
        pygame.display.flip()

        if menu != "homeMenu()":
            return ""

def goLoginMenu():
    global menu
    menu = "loginMenu()"

def loginMenu():
    startListenner()

    def loginSend(username, password):
        send(f"login('{username}', '{password}')")

    buttons = [
        Button([10, 10], [5, 5], "DarkGrey", "X", 5, "White", "goHomeMenu()"),
        Button([50, 70], [20, 5], (13, 164, 31), "0013", 4, (255, 255, 255), "loginSend(entries[0].text, entries[1].text)")
    ]

    entries = [
        Entry([50, 30], [20, 5], (26, 118, 200), "0015", 4, "White"),
        Entry([50, 50], [20, 5], (26, 118, 200), "0016", 4, "White")
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "0008", "White"),
            Button([60, 55], [10, 5], "Red", "0009", 4, "White", "escape()"),
            Button([40, 55], [10, 5], "Green", "0010", 4, "White", "popups[0].close()")
        ])
    ]

    texts = [
        Text([50, 10], 8, "0013", "lightBlue"),
        Text([50, 25], 4, "", "Red")
    ]

    run = True
    while run == True:
        char = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                popups[0].open()

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        evaluateData = eval(data)

                for entry in entries:
                    entry.click()

                for popup in popups:
                    data = popup.click()
                    
                    if len(data) != 0:
                        eval(data)

            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] == 1:
                    char = "\b"
                elif pygame.key.get_pressed()[pygame.K_RETURN] == 1:
                    eval(buttons[1].forceClick())
                else:
                    char = event.unicode

        screen.fill(0)

        for button in buttons:
            button.show()

        for entry in entries:
            entry.show(char)

        if len(errorCode) != 0:
            texts[1].setText(trad.trad(errorCode))

        for text in texts:
            text.show()

        for popup in popups:
            popup.show()

        pygame.display.flip()

        if menu != "loginMenu()":
            return ""

def goSigninMenu():
    global menu
    menu = "signinMenu()"

def signinMenu():
    startListenner()

    def signinSend(username, password, confirmation):
        send(f"signin('{username}', '{password}', '{confirmation}')")

    buttons = [
        Button([10, 10], [5, 5], "DarkGrey", "X", 5, "White", "goHomeMenu()"),
        Button([50, 80], [20, 5], (13, 164, 31), "0014", 4, "White", "signinSend(entries[0].text, entries[1].text, entries[2].text)")
    ]

    entries = [
        Entry([50, 20], [20, 5], (26, 118, 200), "0015", 4, "White"),
        Entry([50, 40], [20, 5], (26, 118, 200), "0016", 4, "White"),
        Entry([50, 60], [20, 5], (26, 118, 200), "0018", 4, "White"),
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "0008", "White"),
            Button([60, 55], [10, 5], "Red", "0009", 4, "White", "escape()"),
            Button([40, 55], [10, 5], "Green", "0010", 4, "White", "popups[0].close()")
        ])
    ]

    texts = [
        Text([50, 10], 8, "0014", "lightBlue"),
        Text([50, 15], 4, "", "Red")
    ]

    run = True
    while run == True:
        char = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                popups[0].open()

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        evaluateData = eval(data)

                for entry in entries:
                    entry.click()

                for popup in popups:
                    data = popup.click()
                    
                    if len(data) != 0:
                        eval(data)

            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] == 1:
                    char = "\b"
                elif pygame.key.get_pressed()[pygame.K_RETURN] == 1:
                    eval(buttons[1].forceClick())
                else:
                    char = event.unicode

        screen.fill(0)

        for button in buttons:
            button.show()

        for entry in entries:
            entry.show(char)

        if len(errorCode) != 0:
            texts[1].setText(trad.trad(errorCode))

        for text in texts:
            text.show()

        for popup in popups:
            popup.show()
            
        pygame.display.flip()

        if menu != "signinMenu()":
            return ""

def connectedToGame(verification, code):
    global errorCode, gameCode, menu
    if verification == True:
        gameCode = code
        menu = "waitMenu()"
    else:
        errorCode = code

def login(verification, data):
    global userData, menu, errorCode
    if verification == True:
        userData = data
        menu = "mainMenu()"
    else:
        errorCode = data

def changeTeam(userName):
    pass

def gameStarted():
    pass

def newPlayer(userName):
    pass

def waitMenu():
    global players
    players = {}

    buttons = [
        Button([85, 90], [18, 5], (13, 164, 31), "0006", 4, "White", "send('startGame()')"),
        Button([50, 90], [18, 5], "lightBlue", "0007", 4, "White", "send('changeTeam()')")
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "0008", "White"),
            Button([60, 55], [10, 5], "Red", "0009", 4, "White", "escape()"),
            Button([40, 55], [10, 5], "Green", "0010", 4, "White", "popups[0].close()")
        ])
    ]

    run = True
    while run == True:
        char = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                popups[0].open()

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        evaluateData = eval(data)
                        
                for popup in popups:
                    data = popup.click()
                    
                    if len(data) != 0:
                        eval(data)

            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] == 1:
                    char = "\b"
                else:
                    char = event.unicode

        screen.fill(0)

        for button in buttons:
            button.show()

        for popup in popups:
            popup.show(char)

        pygame.display.flip()

        if menu != "waitMenu()":
            return ""

def mainMenu():
    errorCode = ""
    buttons = [
        Button([85, 90], [18, 5], (13, 164, 31), "0006", 4, "White", "popups[1].open()"),
        Button([65, 90], [18, 5], (6, 130, 212), "0011", 3, "White", "createGameSend()")
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "0008", "White"),
            Button([60, 55], [10, 5], "Red", "0009", 4, "White", "escape()"),
            Button([40, 55], [10, 5], "Green", "0010", 4, "White", "popups[0].close()")
        ]),
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "0012", "White"),
            Entry([45, 55], [20, 5], (26, 118, 200), "XXXXXX", 4, "White"),
            Button([60, 55], [5, 5], "DarkGreen", "0006", 4, "White", "connectToGameSend(popups[1].components[2].text)")
        ])
    ]

    texts = [
        Text([50, 25], 4, "", "Red")
    ]

    def createGameSend():
        send("createGame()")

    def connectToGameSend(code):
        send(f"connectToGame('{code}')")
        popups[1].close()

    run = True
    while run == True:
        char = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                popups[0].open()
            
            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        evaluateData = eval(data)

                for popup in popups:
                    data = popup.click()
                    
                    if len(data) != 0:
                        eval(data)

            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] == 1:
                    char = "\b"
                else:
                    char = event.unicode

        screen.fill(0)

        if len(errorCode) != 0:
            texts[0].setText(trad.trad(errorCode))

        for text in texts:
            text.show()

        for button in buttons:
            button.show()

        for popup in popups:
            popup.show(char)

        pygame.display.flip()

        print(menu)
        time.sleep(0.1)
        if menu != "mainMenu()":
            return ""

run = True
while run == True:
    menuReturn = eval(menu)