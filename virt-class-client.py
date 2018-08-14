###########################
# virt-class-client.py
# handles whiteboard features
# adileo
###########################

# GLOBAL REFERENCES
###########################
# (1) https://stackoverflow.com/questions/
# 44099594/how-to-make-a-tkinter-canvast-rectangle-with-rounded-corners?rq=1
# (2) https://stackoverflow.com/questions/22925599/mouse-position-python-tkinter
# (3) https://kdchin.gitbooks.io/sockets-module-manual/content/
# (4) http://www.cs.cmu.edu/~112n18/notes/notes-animations-part2.html
# (5) http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/create_line.html
# (6) Tkinter fix for B1Motion causing stack overflow provided by Zoe
# (7) https://github.com/jarvisteach/tkinter-png
###########################

# Animation Starter Code from 112 site

from tkinter import *
from tkinter import filedialog
import math
import tkinter_png
import socket
import threading
from queue import Queue
from whiteboard import *

###########################
# Client-Server Code
###########################
# HOST = "172.24.140.6"
HOST = "127.0.0.1"
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")


class Struct(object): pass

def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")


###########################
# Helper Functions
###########################

def convertImages(imgs):
    for img in imgs:
        img.convert()

###########################
# Main Functions
###########################

def init(data):
    data.whiteboard = Whiteboard()
    data.brush = Brush("One Sad, Alone & Unconnected Brush")
    data.stroke = Stroke()
    data.cursor = Struct()

    data.currentTool = "brush"
    data.prevTool = "brush"
    # stores all necessary details to draw specific tools/their features
    data.strokes = list()
    data.toolPos = dict()
    data.shapePos = list()
    data.imagePos = list()
    data.textPos = list()
    data.otherClients = dict()
    data.myID = None

    data.whosDrawing = dict()
    convertImages(data.whiteboard.imgs)
    data.whiteboard.fillLeftDivider(data,data.whiteboard.numTools,
                                    data.whiteboard.boxLen)
    data.cursor.r = 5
    data.cursor.x,data.cursor.y = -10,-10

    data.isMousePressed = False
    data.audio = False

    data.colorChooser = ColorChooser()
    data.shapes = Shapes(data)
    #anchor is starting point for shape and end is once last click is processed
    data.anchorX, data.anchorY, data.endX, data.endY = None, None, None, None
    # isAnchored - is point anchored yet?
    # selectedShape - has a shape been selected yet?
    # have we finished the shape by getting to populate end data fields?
    data.shape,data.isAnchored,data.selectedShape,data.finishedShape = None, False, False, False

    data.image = Image()
    # have we selected the img yet?
    data.selectedImage = False
    # have we selected point for img yet?
    data.finishedImage = False

    data.text = None
    # finishedText - have we stopped typing and selected a point for placement?
    # selectedText - once text has been finished and entered
    # isTyping - is the user typing?
    data.finishedText, data.selectedText, data.isTyping = False, False, False
    data.nextStep = False

def mousePressed(event, data, root):
    data.whiteboard.getCurrentTool(event, data, root)
    data.shapes.getCurrentShape(event,data)

    if data.currentTool == "shapes" and data.shapes.currentShape != None:
        if not data.isAnchored and data.selectedShape and not data.finishedShape:
            data.anchorX, data.anchorY = event.x, event.y
            data.shape = Shape(data.anchorX, data.anchorY, event.x, event.y,
                               data.shapes.currentShape, data.brush.color)
            data.isAnchored = True
        elif data.isAnchored:
            data.finishedShape = True
        data.selectedShape = True

    if data.currentTool == "image":
        if not data.finishedImage and data.selectedImage:
            data.image.x = event.x
            data.image.y = event.y
            data.currentTool = "brush"
            data.finishedImage = True
        data.selectedImage = True

    if data.currentTool == "text" and data.nextStep:
            data.text = TextBox(event.x,event.y,data.brush.color, "")
            data.isTyping = True
            data.selectedText = True
    data.nextStep = True


def mouseReleased(event, data):
    if data.finishedShape and data.isAnchored:
        data.shape.x1 = event.x
        data.shape.y1 = event.y
        data.shapePos.append(data.shape)
        msg = "spawnShape %s %f %f %f %f %s\n" % (data.shape.shape, data.shape.x0,data.shape.y0,
                                                 data.shape.x1,data.shape.y1,data.shape.color)
        print("sending: ", msg)
        data.server.send(msg.encode())

        data.shape.finishShape(data)
    if data.finishedImage:
        data.image.filePath = data.image.filePath.replace(" ", "|")
        data.imagePos.append(data.image)
        msg = "spawnImage %s %f %f\n" % (data.image.filePath, data.image.x,data.image.y)
        print("sending: ",msg)
        data.server.send(msg.encode())
        data.selectedImage = False
        data.finishedImage = False
        data.image = Image()
        data.currentTool = "brush"


def keyPressed(event, data):
    print(event.keysym)
    if event.keysym == "bracketleft":
        data.brush.changeSize(data, -2)
    elif event.keysym == 'bracketright':
        data.brush.changeSize(data, 2)

    if data.currentTool == "text" and data.isTyping and data.text != None:
        if event.keysym == "Return":
            data.isTyping = False
            data.selectedText = True
        elif event.keysym == "BackSpace":
            data.text.text = data.text.text[:len(data.text.text)-1]
        else:
            data.text.text += event.char

def timerFired(data):
    if data.text != None:
        if not data.finishedText and data.selectedText and not data.isTyping:
            data.text.text = data.text.text.replace(" ","|")
            data.finishedText = True
            msg = "text %f %f %s %s\n" % (data.text.x,data.text.y, data.brush.color,data.text.text)
            print("sending: ", msg)
            data.server.send(msg.encode())

    if data.finishedText:
        #appending text
        data.text.text = data.text.text.replace("|", " ")
        data.textPos.append(data.text)
        data.selectedText = False
        data.finishedText = False
        data.text = None

    while (serverMsg.qsize() > 0):
      msg = serverMsg.get(False)
      try:
        print("received: ", msg, "\n")
        msg = msg.split()
        command = msg[0]

        if (command == "newStroke"):
            newPID = msg[1]
            details = msg[2:]
            data.strokes.append(list())
            for point in details:
                data.strokes[-1].append(eval(point))

        elif (command == "myIDis"):
            myPID = msg[1]
            data.myID = myPID
            data.brush.changePID(myPID)

        elif (command == "brush"):
            whichStroke = data.whosDrawing[msg[1]]
            data.strokes[whichStroke].append(eval(msg[2]))

        elif (command == "brushStart"):
            data.whosDrawing[msg[1]] = len(data.strokes)
            data.strokes.append(list())

        elif (command == "brushEnd"):
            data.whosDrawing[msg[1]] = False

        elif (command == "spawnShape"):
            shape = msg[2]
            x0,y0 = float(msg[3]),float(msg[4])
            x1,y1 = float(msg[5]),float(msg[6])
            color = msg[7]
            newShape = Shape(x0,y0,x1,y1,shape,color)
            data.shapePos.append(newShape)
        elif command == "spawnImage":
            filePath = msg[2]
            filePath = filePath.replace("|", " ")
            x = float(msg[3])
            y = float(msg[4])
            newImage = Image()
            newImage.filePath = filePath
            newImage.x,newImage.y = x,y
            newImage.tkImage = PhotoImage(file=newImage.filePath)
            data.imagePos.append(newImage)

        elif command == "text":
            x = float(msg[2])
            y = float(msg[3])
            color = msg[4]
            msg[5] = msg[5].replace("|"," ")
            text = msg[5]
            newText = TextBox(x,y,color,text)
            data.textPos.append(newText)

      except:
        print("failed")
      serverMsg.task_done()


def motion(event,data):
    data.cursor.x,data.cursor.y = event.x,event.y
    if data.currentTool == "shapes" and data.isAnchored:
        data.shape.x1 = event.x
        data.shape.y1 = event.y

def b1Motion(event, data):
    msg = ""

    if data.strokes != [] and data.strokes[-1] != []\
        and data.currentTool == "brush":
        if not data.isMousePressed:
            data.isMousePressed = True
            msg = "brushStart\n"
            data.server.send(msg.encode())
        msg = "brush"
        msg += " "+str(data.strokes[-1][-1]).replace(" ", "")
        msg += "\n"

    if msg != "":
        print ("sending: ", msg)
        data.server.send(msg.encode())

def redrawAll(canvas, data, root):
    for shape in data.shapePos:
        shape.draw(canvas)
    for image in data.imagePos:
        image.draw(canvas)
    for text in data.textPos:
        text.draw(canvas)
    data.brush.drawStrokes(canvas, data)
    if data.currentTool == "brush":
        data.brush.drawBrushRadius(canvas, data)
    if data.currentTool == "shapes" and data.shapes.currentShape != None and data.isAnchored:
        data.shape.draw(canvas)
    if data.currentTool == "shapes":
        data.shapes.drawExtendedMenu(canvas)
        data.shapes.showSelectedShape(canvas)
        data.shapes.drawIcons(canvas)
    if data.currentTool == "text" and data.isTyping == True and data.text != None:
        data.text.draw(canvas)
    data.whiteboard.drawLeftDivider(canvas)
    data.whiteboard.showSelectedTool(canvas, data)
    data.whiteboard.drawLeftTools(canvas, data)

# template from source 3+4

def run(width=300, height=300,serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data, root):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data, root)
        canvas.update()

    def motionWrapper(motion, event,canvas,data):
        if data.mouseWrapperMutex: return
        data.mouseWrapperMutex = True
        motion(event,data)
        redrawAllWrapper(canvas,data, root)
        data.mouseWrapperMutex = False

    def mousePressedWrapper(event,canvas,data, root):
        mousePressed(event,data, root)
        redrawAllWrapper(canvas,data, root)

    #  source 6
    def mouseWrapper(mouseFn, event, canvas, data):
        if data.mouseWrapperMutex: return
        data.mouseWrapperMutex = True
        data.stroke.draw(event,data)
        mouseFn(event, data)
        redrawAllWrapper(canvas, data, root)
        data.mouseWrapperMutex = False

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data, root)

    def mouseReleaseWrapper(event, canvas, data):
        mouseReleased(event, data)
        if data.isMousePressed:
            data.isMousePressed = False
            msg = "brushEnd\n"
            data.server.send(msg.encode())
        data.stroke.reset()

    def timerFiredWrapper(canvas, data, root):
        timerFired(data)
        redrawAllWrapper(canvas, data, root)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data, root)

    # Set up data and call init
    data = Struct()
    data.mouseWrapperMutex = False
    data.server = server
    data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 1 # milliseconds
    root = Tk()
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()

    # set up events

    root.bind("<ButtonPress-1>", lambda event:
                            mousePressedWrapper(event,canvas,data, root))
    root.bind("<KeyPress>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind('<Motion>', lambda event:
                            motionWrapper(motion, event,canvas,data))
    root.bind('<B1-Motion>', lambda event:
                                mouseWrapper(b1Motion, event,canvas,data))
    root.bind('<ButtonRelease-1>', lambda event: mouseReleaseWrapper\
    (event, canvas,data))
    timerFiredWrapper(canvas, data, root)

    root.title("Virtual Classroom")

    root.mainloop()
    print("bye!")

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

run(500, 500, serverMsg, server)