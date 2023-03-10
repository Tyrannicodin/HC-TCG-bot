from math import log2
from typing import Iterable
from PIL import Image, ImageDraw, ImageFont

Color = tuple[int, int, int]

def mean(values:Iterable) -> float:
    return sum(values)/len(values)

class colors:
    GRAY = (72, 72, 72, 255)
    CYAN = (30, 126, 133, 255)
    WHITE = (255, 255, 255, 255)
    GOLD = (161, 135, 0, 255)

class brackets:
    FONT = ImageFont.truetype("Helvetica.ttf", size=10)
    DEFAULT_PLAYERNAMES = {
        0: ""
    }

    boxHeight = 50
    boxWidth = 100
    paddingY = 20
    paddingX = 20

    def __init__(self, players: list[int], playerNames:list[str]):
        n = len(players)
        self.layerCount = log2(n)
        if not self.layerCount.is_integer():
            raise NotImplementedError("Players must be a power of 2")
        self.layerCount = int(self.layerCount)

        self.playerNames = self.DEFAULT_PLAYERNAMES
        self.playerNames.update({(players[i], playerNames[i]) for i in range(n)})

        self.layer = [(players[i], players[i + 1]) for i in range(0, n, 2)]
        self.nextPlayers = [0 for _ in range(len(self.layer))]
        self.layers = []

    def declareWinner(self, winner:int):
        for i, tup in enumerate(self.layer):
            if winner in tup:
                self.nextPlayers[i] = winner
                break
        self.updateLayer()
    
    def declareLoser(self, loser:int):
        for i, tup in enumerate(self.layer):
            if loser in tup:
                manip = list(tup)
                self.nextPlayers[i] = manip.pop(0 if manip.index(loser) == 1 else 1)
                break
        self.updateLayer()

    def updateLayer(self):
        completedPlayers = len([num for num in self.nextPlayers if num != 0])
        if len(self.layer) == completedPlayers:
            if completedPlayers == 1:
                self.layers.append(self.layer)
                self.layer = self.nextPlayers[0]
                self.layers.append([self.layer])
                return
            self.layers.append(self.layer)
            self.layer = [(self.nextPlayers[i], self.nextPlayers[i + 1]) for i in range(0, len(self.nextPlayers), 2)]
            self.nextPlayers = [0 for _ in range(len(self.layer))]

    def newLineText(self, text:str):
        line = ""
        final = ""
        for char in text:
            if self.FONT.getsize(line + char)[0] > self.boxWidth:
                final += line + "\n"
                line = ""
            else:
                line += char
        return final + line
    
    def createRect(self, text:str, color:Color, textCol:Color) -> Image.Image:
        im = Image.new("RGBA", (self.boxWidth, self.boxHeight))
        imDraw = ImageDraw.Draw(im)
        imDraw.rounded_rectangle(((0,0), im.size), 15, color)
        imDraw.multiline_text((im.width//2, im.height//2), self.newLineText(text), textCol, self.FONT, "mm", align="center")
        return im

    def render(self, bg:Color = colors.GRAY, fg:Color = colors.CYAN, text:Color = colors.WHITE, lines:Color = colors.WHITE) -> Image.Image:
        im = Image.new("RGBA", ((self.layerCount+1)*(self.boxWidth+self.paddingX)+self.paddingX, 2**self.layerCount*(self.boxHeight+self.paddingY)+self.paddingY), bg)
        imDraw = ImageDraw.Draw(im, "RGBA")
        layers = [self.layers[i] if i < len(self.layers) else ([0] if i == self.layerCount else ([[0, 0] for _ in range(2**(self.layerCount-i)//2)] if i == len(self.layers)-1 else self.layer)) for i in range(self.layerCount+1)]
        connections = []
        for l, layer in enumerate(layers):
            x = l*(self.boxWidth+self.paddingX) + self.paddingX
            prevConnections = connections
            connections = []

            if l == self.layerCount:
                toPaste = self.createRect(self.playerNames[layer[0]], colors.GOLD, text)
                im.paste(toPaste, (x, prevConnections[0]), toPaste)
                continue
            for i, pair in enumerate(layer):
                toPaste = self.createRect(self.playerNames[pair[0]], fg, text)
                toPaste2 = self.createRect(self.playerNames[pair[1]], fg, text)


                tl1 = i*2*(self.boxHeight+self.paddingY)+self.paddingY if len(prevConnections)/2 != len(layer) else prevConnections[i*2]
                tl2 = (i*2+1)*(self.boxHeight+self.paddingY)+self.paddingY if len(prevConnections)/2 != len(layer) else prevConnections[i*2+1]
                avgPos = int(mean((tl1, tl2)))
                connections.append(avgPos)

                imDraw.line((x+self.boxWidth, tl1+self.boxHeight//2,
                             x+self.boxWidth+self.paddingX//2, tl1+self.boxHeight//2,
                             x+self.boxWidth+self.paddingX//2, tl2+self.boxHeight//2,
                             x+self.boxWidth, tl2+self.boxHeight//2), lines, 5, "curve")
                imDraw.line((x+self.boxWidth+self.paddingX//2, avgPos+self.boxHeight//2,
                             x+(self.boxWidth+self.paddingX), avgPos+self.boxHeight//2), lines, 5, "curve")
                im.paste(toPaste, (x, tl1), toPaste)
                im.paste(toPaste2, (x, tl2), toPaste2)
        return im

if __name__ == "__main__":
    from random import choice

    n = 8

    bracket = brackets(
            [i for i in range(1, n+1)],
            [str(i) for i in range(1, n+1)])
    
    outcomes = [bracket.declareWinner, bracket.declareLoser]

    while type(bracket.layer) != int:
        for pair in bracket.layer:
            choice(outcomes)(pair[0])

    bracket.render().save("image.png")