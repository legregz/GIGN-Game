import socket, pygame, select, time
from threading import Thread

SERVER_HOST = "localhost"
SERVER_PORT = 55352

online = False
offline = False

def connect():
    global online, offline, clientSocket
    while online != True and offline != True:
        try:
            clientSocket = socket.socket()
            clientSocket.connect((SERVER_HOST, SERVER_PORT))
            online = True
        except:
            pass
        time.sleep(5)

connecter = Thread(target = connect, args = ())
connecter.daemon = True
connecter.start()

pygame.init()
screen = pygame.display.set_mode()
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
pygame.key.set_repeat(500, 100)

userData = {}

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

def socketListen():
    read_sockets, write_socket, error_socket = select.select([clientSocket],[],[])

    for socks in read_sockets:
        if socks == clientSocket:
            try:
                msgs = separate(socks.recv(2048).decode())
            except:
                print("Connexion interrompue")

            for msg in msgs:
                if msg[0] == "[" and msg[-1] == "]":
                    return eval(msg)

colorDict = {
    "Cyan": (0, 255, 255),
    "darkCyan": (0, 230, 230),
    "Violet": (255, 0, 255),
    "darkViolet": (230, 0, 230),
    "Yellow": (255, 255, 0),
    "darkYellow": (230, 230, 0),
    "Green": (0, 255, 0),
    "darkGreen": (0, 230, 0),
    "Red": (255, 0, 0),
    "darkRed": (230, 0, 0),
    "Blue": (0, 0, 255),
    "darkBlue": (0, 0, 230),
    "Black" : (0, 0, 0),
    "lightBlue": (0, 177, 255),
    "Grey": (100, 100, 100),
    "darkGrey":(80, 80, 80),
    "White": (255, 255, 255),
    "Orange":(236, 131, 0)
}

def nosign(number):
    if number < 0:
        return 0
    else:
        return number

def createColor(color):
    if type(color) == str():
        return colorDict[color]
    else:
        return color
    
def dark(color):
    if type(color) == str:
        return "dark" + color
    else:
        return (nosign(color[0] - 20), nosign(color[1] - 20), nosign(color[2] - 20))

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
        self.setText(text)
        try:
            self.setPosition(position)
        except:
            pass

    def setPosition(self, position):
        self.position = position
        self.rects = [createRect([self.position[0], self.position[1] + i * (1 + self.texts[i].get_height() / screen.get_height() * 100) - (len(self.texts) - 1) * self.texts[i].get_height() / screen.get_height() * 100], [self.texts[i].get_width() / screen.get_width() * 100, self.texts[i].get_height() / screen.get_height() * 100]) for i in range(len(self.texts))]

    def setText(self, text):
        start = 0
        self.texts = []
        for end in range(len(text) - 1):
            if text[end: end+2] == "//":
                self.texts.append(text[start: end])
                start = end + 2

            elif end == len(text) - 2:
                self.texts.append(text[start: end+2])

        self.texts = [self.font.render(txt, False, createColor(self.color)) for txt in self.texts]

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

        self.Rect = Rect(position, size, color, 0.5)
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
        
class Invitation:
    def __init__(self, size, color, textColor, playerName, fontSize = 4):
        self.playerName = playerName
        self.size = size
        self.components = [
            Rect([], size, color),
            Text([], fontSize, "You have been invite by:", textColor),
            Text([], fontSize, playerName, textColor),
            Button([], [self.size[0] // 4, self.size[0] // 4], "Green", "_/", fontSize, "White", "self.accept()"),
            Button([], [size[0] // 4, size[0] // 4], "Red", "X", fontSize, "White", "self.refuse()")
        ]

    def show(self):
        for elt in self.components:
            elt.show()

    def setPosition(self, position):
        self.position = position
        positions = [
            position,
            [position[0] - self.size[0] // 4, position[1] - self.size[1] // 4],
            [position[0] - self.size[0] // 4, position[1] + self.size[1] // 4],
            [position[0] + self.size[0] // 8 * 3, position[1]],
            [position[0] + self.size[0] // 8, position[1]],
        ]
        for i in range(5):
            self.components[i].setPosition(positions[i])

    def click(self):
        accept = self.components[3].click()
        refuse = self.components[4].click()
        action = max(accept, refuse)
        if action != "":
            try:
                eval(action)
            except:
                pass

    def accept(self):
        clientSocket.send(bytes(str(["acceptInvitation", self.playerName]), "utf-8"))
        """while True:
            message = socketListen()
            if len(message) > 0:
                pass"""

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
                    elt.show()
                except:
                    elt.show(char)

    def open(self):
        self.active = True
        self.delay = time.time() + 0.2

    def close(self):
        self.active = False

def home():
    buttons = [
        Button([85, 90], [20, 5], "Grey", "Offline Mode", 4, "White", "offlineConnect()"),
        Button([50, 40], [20, 5], (13, 164, 31), "Connexion", 4, "White", "login()"),
        Button([50, 60], [20, 5], (13, 164, 31), "Inscription", 4, "White", "signin()")
    ]

    texts = [
        Text([50, 20], 8, "G.I.G.N", "lightBlue"),
        Text([50, 50], 5, "Attention! Il semblerai que vous ne soyez plus// connectes au services du GIGN...//verifiez votre connexion...", "Orange")
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "Voulez-vous vraiment//quitter?", "White"),
            Button([60, 55], [10, 5], "Red", "Oui", 4, "White", "quit()"),
            Button([40, 55], [10, 5], "Green", "Non", 4, "White", "popups[0].close()")
        ])
    ]

    def quitConfirmation():
        popups[0].open()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                quitConfirmation()

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()

                    if len(data) != 0:
                        evaluateData = eval(data)
                        if evaluateData == "connected":
                            return "connected"
                        
                for popup in popups:
                    data = popup.click()

                    if len(data) != 0:
                        eval(data)

        screen.fill(0)

        if online == False:
            texts[1].show()
            buttons[0].active = True
            for i in range(1, 3):
                buttons[i].active = False
        else:
            buttons[0].active = False
            for i in range(1, 3):
                buttons[i].active = True

        for button in buttons:
            button.show()

        for popup in popups:
            popup.show()

        texts[0].show()
            
        pygame.display.flip()

def offlineConnect():
    offline = True
    return "connected"

def loginSend(username, password):
    global userData
    clientSocket.send(bytes(str(["login", username, password]), "utf-8"))
    while True:
        message = socketListen()
        if len(message) > 0:
            if message[0] == "login":
                if message[1] == True:
                    userData = message[2]
                    print(userData)
                    return "connected"
                if message[1] == False:
                    return message[2]

def login():
    buttons = [
        Button([50, 70], [20, 5], (13, 164, 31), "Connexion", 4, (255, 255, 255), "loginSend(entries[0].text, entries[1].text)")
    ]

    entries = [
        Entry([50, 30], [20, 5], (26, 118, 200), "Username", 4, "White"),
        Entry([50, 50], [20, 5], (26, 118, 200), "Password", 4, "White")
    ]

    texts = [
        Text([50, 25], 4, "", "Red")
    ]

    run = True
    while run == True:
        char = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                return "quit"

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        evaluateData = eval(data)
                        if evaluateData == "connected":
                            return "connected"
                        else:
                            texts[0].setText(evaluateData)

                for entry in entries:
                    entry.click()

            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] == 1:
                    char = "\b"
                else:
                    char = event.unicode

        screen.fill(0)

        for button in buttons:
            button.show()

        for entry in entries:
            entry.show(char)

        for text in texts:
            text.show()
            
        pygame.display.flip()

def signinSend(username, password, confirmation):
    global userData
    clientSocket.send(bytes(str(["signin", username, password, confirmation]), "utf-8"))
    while True:
        message = socketListen()
        if len(message) > 0:
            if message[0] == "signin":
                if message[1] == True:
                    userData = message[2]
                    print(userData)
                    return "connected"
                if message[1] == False:
                    return message[2]

def signin():
    buttons = [
        Button([50, 80], [20, 5], (13, 164, 31), "Inscription", 4, "White", "signinSend(entries[0].text, entries[1].text, entries[2].text)")
    ]

    entries = [
        Entry([50, 20], [20, 5], (26, 118, 200), "Username", 4, "White"),
        Entry([50, 40], [20, 5], (26, 118, 200), "Password", 4, "White"),
        Entry([50, 60], [20, 5], (26, 118, 200), "Confirm", 4, "White"),
    ]

    texts = [
        Text([50, 15], 4, "", "Red")
    ]

    run = True
    while run == True:
        char = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                return "quit"

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        evaluateData = eval(data)
                        if evaluateData == "connected":
                            return "connected"
                        else:
                            texts[0].setText(evaluateData)

                for entry in entries:
                    entry.click()

            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_BACKSPACE] == 1:
                    char = "\b"
                else:
                    char = event.unicode

        screen.fill(0)

        for button in buttons:
            button.show()

        for entry in entries:
            entry.show(char)

        for text in texts:
            text.show()
            
        pygame.display.flip()

def social():
    buttons = [
        Button([80, 95], [18, 5], (13, 164, 31), "Inviter", 4, "White", "openInvite()")
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 45], 4, "Qui voulez-vous inviter?", "White"),
            Entry([50, 50], [20, 5], (26, 118, 200), "Nom du joueur", 4, "White"),
            Button([60, 55], [5, 4], "Green", "Envoyer", 4, "White", "invite(popups[0].components[1].text)")
        ]),
        PopUp([50, 50], [35, 10], "Grey", [
            Text([50, 50], 4, "Impossible, mode hors ligne", "White"),
        ])
    ]

    if online == True:
        ScrollableLists = [
            ScrollableList([80, 45], [20, 90], [Invitation([18, 15], "Grey", "White", name) for name in userData["invitations"]])
        ]

    def openInvite():
        if online == True:
            popups[0].open()
        else:
            popups[1].open()

    def invite(playerName):
        clientSocket.send(bytes(str(["invite", playerName]), "utf-8"))
        popups[0].close()

    run = True
    while run == True:
        char = ""

        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                return "quit"

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        eval(data)

                for popup in popups:
                    data = popup.click()

                    if len(data) != 0:
                        eval(data)

                if online == True:
                    for scrollable in ScrollableLists:
                        data = scrollable.click()

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

        if online == True:
            for scrollable in ScrollableLists:
                scrollable.show()
            
        pygame.display.flip()

def menuListen():
    global run
    while run == True:
        msg = socketListen()
        if len(msg) > 0:
            if msg[0] == "invited":
                userData["invitations"].append(msg[1])


def main():
    def invitations():
        if online == True:
            return len(userData["invitations"])
        else:
            return 0

    buttons = [
        Button([85, 90], [18, 5], (13, 164, 31), "Jouer", 4, "White", "play()"),
        Button([65, 90], [18, 5], (13, 164, 31), "Social", 4, "White", "social()", invitations())
    ]

    popups = [
        PopUp([50, 50], [35, 20], "Grey", [
            Text([50, 48], 4, "Voulez-vous vraiment//quitter?", "White"),
            Button([60, 55], [10, 5], "Red", "Oui", 4, "White", "quit()"),
            Button([40, 55], [10, 5], "Green", "Non", 4, "White", "popups[0].close()")
        ])
    ]

    def quitConfirmation():
        popups[0].open()

    run = True
    while run == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                quitConfirmation()
            
            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    data = button.click()
                    
                    if len(data) != 0:
                        eval(data)

                for popup in popups:
                    data = popup.click()
                    
                    if len(data) != 0:
                        eval(data)

        if online == True:
            buttons[1].notify(len(userData["invitations"]))

        screen.fill(0)

        for button in buttons:
            button.show()

        for popup in popups:
            popup.show()

        pygame.display.flip()

run = True
while run == True:
    homeMenu = home()
    if homeMenu == "connected":
        if online == True:
            listener = Thread(target = menuListen, args = ())
            listener.daemon = True
            listener.start()

        mainMenu = main()
        if mainMenu == "quit":
            run = False
    elif homeMenu == "quit":
        run = False