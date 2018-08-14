###########################
# whiteboard.py
# contains whiteboard features
# adileo
###########################

from tkinter import *
import math
import tkinter_png
from tkinter.colorchooser import askcolor
from tkinter import filedialog


class Whiteboard(object):
    def __init__(self):
        self.margin = 10
        self.wOfToolbox = 60
        self.hOfToolbox = 350
        self.numTools = 6
        self.boxLen = 30
        # source 7
        self.imgs = [tkinter_png.PngImageTk("img/brush.png"),
                     tkinter_png.PngImageTk("img/color.png"),
                     tkinter_png.PngImageTk("img/shape.png"),
                     tkinter_png.PngImageTk("img/text.png"),
                     tkinter_png.PngImageTk("img/image.png"),
                     tkinter_png.PngImageTk("img/audio_off.png"),
                     tkinter_png.PngImageTk("img/audio_on.png")]
        self.tools = ["brush", "color", "shapes", "text", "image", "audio"]

    def drawRoundedRectangle(self, canvas, x1, y1, x2, y2, radius, color):
        # taken from source 1
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        canvas.create_polygon(points, smooth=True, fill=color)

    # draws border toolbox
    def drawLeftDivider(self, canvas):
        x1 = self.margin
        y1 = self.margin + self.wOfToolbox
        x2 = x1 + self.wOfToolbox
        y2 = y1 + self.hOfToolbox
        radius = self.wOfToolbox / 2
        color = "lightgray"
        self.drawRoundedRectangle(canvas, x1, y1, x2, y2, radius, color)

    # fills tool box with respective tools and stores locations
    def fillLeftDivider(self, data, numB, boxLen):
        r = boxLen / 2
        m = (self.wOfToolbox - 2 * r) / 2
        cx = self.margin + r + m
        sp = (self.hOfToolbox - numB * boxLen) / (numB + 1)
        cy = self.margin + sp + r + self.wOfToolbox
        for i in range(numB):
            data.toolPos[self.tools[i]] = (cx, cy, r)
            cy = cy + sp + 2 * r

    # draws tools with images
    def drawLeftTools(self, canvas, data):
        for i in range(len(data.toolPos)):
            if not data.audio:
                canvas.create_image(data.toolPos[self.tools[i]][0],
                                    data.toolPos[self.tools[i]][1],
                                    image=self.imgs[i].image)
            else:
                if self.tools[i] == "audio":
                    canvas.create_image(data.toolPos[self.tools[i]][0],
                                        data.toolPos[self.tools[i]][1],
                                        image=self.imgs[i + 1].image)
                else:
                    canvas.create_image(data.toolPos[self.tools[i]][0],
                                        data.toolPos[self.tools[i]][1],
                                        image=self.imgs[i].image)

    # gets current tool using circle collisions
    def getCurrentTool(self, event, data, root):
        data.prevTool = data.currentTool
        for i in range(len(data.toolPos)):
            if self.cirCirCollision(data.toolPos[self.tools[i]][0], \
                               data.toolPos[self.tools[i]][1],event.x,event.y,\
                               data.toolPos[self.tools[i]][2], 0):
                data.currentTool = self.tools[i]

        if data.currentTool == "audio":
            data.audio = not data.audio
            data.currentTool = data.prevTool

        if data.currentTool == "color":
            data.colorChooser.changeColor(data)
            data.currentTool = data.prevTool

        if data.currentTool == "image" and data.image.filePath == None:
            data.image.browse(root)

    # from hw1
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def cirCirCollision(self, x1, y1, x2, y2, r1, r2):
        return self.distance(x1, y1, x2, y2) <= r1 + r2

    def rectCirCollision(self, cx, cy, x1, y1, x2, y2):
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return True
        return False

    def showSelectedTool(self, canvas, data):
        # (cx,cy,r)
        currentTool = data.toolPos[data.currentTool]
        xMargin = 5
        r = currentTool[2]
        x0 = currentTool[0] - r
        y0 = currentTool[1] - r
        x1 = currentTool[0] + r
        y1 = currentTool[1] + r
        selectionRect = (x0 - xMargin, y0 - xMargin, x1 + xMargin, y1 + xMargin)
        self.drawRoundedRectangle(canvas, selectionRect[0], selectionRect[1],
                             selectionRect[2], selectionRect[3], r + xMargin,
                             "gray")

class Brush(Whiteboard):
    def __init__(self, PID):
        self.color = "black"
        self.ID = PID
        self.isDrawing = False

    def changePID(self, newPID):
        self.ID = newPID

    def changeSize(self, data, dr):
        data.cursor.r += dr
        if data.cursor.r < 5: data.cursor.r = 5

    def drawBrushRadius(self, canvas, data):
        cxc = data.cursor.x
        cyc = data.cursor.y
        r = data.cursor.r
        x1 = data.whiteboard.margin
        y1 = data.whiteboard.margin + data.whiteboard.wOfToolbox
        x2 = x1 + data.whiteboard.wOfToolbox
        y2 = y1 + data.whiteboard.hOfToolbox
        if not self.rectCirCollision(cxc, cyc, x1, y1, x2, y2):
            canvas.create_oval(cxc - r, cyc - r, cxc + r, cyc + r,
                               outline="black")

    def drawStrokes(self, canvas, data):
        for i in range(0, len(data.strokes)):
            if len(data.strokes[i]) >= 1:
                for j in range(1, len(data.strokes[i])):
                    oldX = data.strokes[i][j-1][0]
                    oldY = data.strokes[i][j-1][1]
                    x = data.strokes[i][j][0]
                    y = data.strokes[i][j][1]
                    #source 5
                    canvas.create_line(oldX, oldY, x, y,
                                       width=data.strokes[i][j][2]*2,
                                       fill=data.strokes[i][j][3],
                                     smooth=TRUE, splinesteps=40, capstyle=ROUND)

class Stroke(Brush):
    def __init__(self):
        self.oldx = None
        self.oldy = None

    def draw(self, event, data):
        data.cursor.x, data.cursor.y = event.x, event.y
        if data.currentTool == "brush":
            if self.oldx != None and self.oldy != None:
                data.strokes[-1].append((event.x, event.y, data.cursor.r,
                                        data.brush.color))
            else:
                data.strokes.append(list())
                self.oldx = event.x
                self.oldy = event.y

    def reset(self):
        self.oldx, self.oldy = None, None

class ColorChooser(object):
    def changeColor(self, data):
        data.brush.color = (askcolor())[1]

class Shapes(Whiteboard):
    def __init__(self, data):
        self.startX = data.toolPos["shapes"][0]+data.toolPos["shapes"][2]*2-10
        self.startY = data.toolPos["shapes"][1]-data.toolPos["shapes"][2]*2+10
        self.startX1 = self.startX + 150
        self.startY1 = self.startY + 40
        self.shapePos = dict()
        self.currentShape = None
        self.shapes = ["circle","square","triangle"]
        self.shapeSize = 25

    def drawIcons(self, canvas):
        wOfBox = self.distance(self.startX,self.startY,self.startX1,self.startY1)
        numIcons = 3
        margin = 5
        sp = ((wOfBox - self.shapeSize*numIcons) / numIcons + 1)
        x = self.startX + 2*margin
        y = self.startY + margin+2
        x1 = x + self.shapeSize
        y1 = y + self.shapeSize
        self.shapePos[self.shapes[0]] = (x,y,x1,y1)
        canvas.create_oval(self.shapePos[self.shapes[0]],fill="black")
        x += sp+self.shapeSize
        x1 += sp +self.shapeSize
        self.shapePos[self.shapes[1]] = (x, y, x1, y1)
        canvas.create_rectangle(self.shapePos[self.shapes[1]],fill="black")
        x += sp+self.shapeSize
        x1 += sp +self.shapeSize
        self.shapePos[self.shapes[2]] = ((x,y+self.shapeSize),(x1,y1),(x+(x1-x)/2,y))
        canvas.create_polygon(self.shapePos[self.shapes[2]])

    def getCurrentShape(self, event, data):
        for k in self.shapePos:
            if k == "circle" or k == "square":
                x0 = self.shapePos[k][0]
                y0 = self.shapePos[k][1]
                x1 = self.shapePos[k][2]
                y1 = self.shapePos[k][3]
            elif k == "triangle":
                x0 = self.shapePos[k][0][0]
                y0 = self.shapePos[k][0][1]-self.shapeSize
                x1 = self.shapePos[k][1][0]
                y1 = self.shapePos[k][1][1]
            if self.rectCirCollision(event.x,event.y,x0,y0,x1,y1):
                data.shapes.currentShape = k

    def showSelectedShape(self, canvas):
        # (cx,cy,r)
        if self.currentShape != None:
            xMargin = 5
            r = self.shapeSize/2
            if self.currentShape == "circle" or self.currentShape == "square":
                x0 = self.shapePos[self.currentShape][0]
                y0 = self.shapePos[self.currentShape][1]
                x1 = self.shapePos[self.currentShape][2]
                y1 = self.shapePos[self.currentShape][3]
            else:
                x0 = self.shapePos[self.currentShape][0][0]
                y0 = self.shapePos[self.currentShape][0][1]-self.shapeSize
                x1 = self.shapePos[self.currentShape][1][0]
                y1 = self.shapePos[self.currentShape][1][1]
            selectionRect = (x0 - xMargin, y0 - xMargin, x1 + xMargin, y1 + xMargin)
            self.drawRoundedRectangle(canvas, selectionRect[0], selectionRect[1],
                                 selectionRect[2], selectionRect[3], r + xMargin,
                                 "gray")

    def drawExtendedMenu(self, canvas):
        super().drawRoundedRectangle(canvas,self.startX,self.startY,self.startX1,self.startY1, 25, "lightgray")

class Shape(object):
    def __init__(self, x0, y0, x1, y1, shape, color):
        self.x0,self.y0,self.x1,self.y1 = x0,y0,x1,y1
        self.shape,self.color = shape, color

    def draw(self, canvas):
        if self.x0 and self.y0 and self.x1 and self.y1:
            if self.shape == "circle":
                canvas.create_oval(self.x0,self.y0,self.x1,self.y1,fill=self.color)
            elif self.shape == "square":
                canvas.create_rectangle(self.x0,self.y0,self.x1,self.y1,fill=self.color)
            else:
                canvas.create_polygon((self.x0,self.y0+(self.y1-self.y0)),(self.x1,self.y1),(self.x0+(self.x1-self.x0)/2,self.y0),fill=self.color)

    def finishShape(self, data):
        data.isAnchored = False
        data.currentTool = data.prevTool
        data.shape = None
        data.finishedShape = False
        data.shapes.currentShape = None
        data.selectedShape = False
        data.anchorX, data.anchorY, data.endX, data.endY = None, None, None, None


class TextBox(Whiteboard):
    def __init__(self, x,y,color, text):
        self.text = text
        self.x,self.y = x,y
        self.color = color

    def draw(self, canvas):
        if self.x and self.y:
            canvas.create_text(self.x,self.y,text=self.text, fill=self.color)


class Image(Whiteboard):
    def __init__(self):
        self.tkImage = None
        self.filePath = None
        self.x, self.y = None, None

    def browse(self, root):
        root.update()
        root.filename = filedialog.askopenfilename(initialdir="/Desktop",
                                                   title="Select file",
                                                   filetypes=[("GIF Files","*.gif")])
        root.update()
        self.filePath = root.filename
        self.tkImage = PhotoImage(file=self.filePath)

    def draw(self, canvas):
        if self.x and self.y:
            canvas.create_image((self.x,self.y),image=self.tkImage)

