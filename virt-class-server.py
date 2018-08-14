###########################
# virt-class-server.py
# handles server features
# adileo
###########################

# sockets template from source 3

import socket
import threading
from queue import Queue

HOST = '127.0.0.1'
PORT = 50003
BACKLOG = 30  # max clients

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(BACKLOG)
print('Looking For Connection')


def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ''
    while True:
        try:
            msg += client.recv(10).decode('UTF-8')
            command = msg.split('\n')
            while len(command) > 1:
                readyMsg = command[0]
                msg = '\n'.join(command[1:])
                serverChannel.put(str(cID) + ' ' + readyMsg)
                command = msg.split('\n')
        except:
            print('failed')
            return


def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        print('msg recv: ', msg)
        msgList = msg.split(' ')
        senderID = msgList[0]
        instruction = msgList[1]
        details = ' '.join(msgList[2:])

        if details != '':

            if instruction == 'brush':
                point = eval(msgList[2])
                strokes[-1].append(point)

                for cID in clientele:
                    sendMsg = instruction + ' ' + senderID + ' ' \
                              + msgList[2] + '\n'
                    clientele[cID].send(sendMsg.encode())
                    print('> sent to %s:' % cID)
            else:
                if instruction == "spawnShape":
                    details = details.split(" ")
                    shape = details[0]
                    x0, y0 = float(details[1]), float(details[2])
                    x1, y1 = float(details[3]), float(details[4])
                    color = details[5]
                    shapes.append((shape, x0, y0, x1, y1, color))
                    details = " ".join(details)
                elif instruction == "spawnImage":
                    details = details.split(" ")
                    filePath = details[0]
                    x = float(details[1])
                    y = float(details[2])
                    images.append((filePath,x,y))
                    details = " ".join(details)
                elif instruction == "text":
                    details = details.split(" ")
                    x,y = float(details[0]),float(details[1])
                    color = details[2]
                    text = details[3]
                    texts.append((x,y,color, text))
                    details = " ".join(details)
                for cID in clientele:
                        sendMsg = instruction + ' ' + senderID + ' ' \
                                  + details + '\n'
                        clientele[cID].send(sendMsg.encode())
                        print('> sent to %s:' % cID, sendMsg[:-1])
        elif instruction == 'brushStart':
            strokes.append(list())
            sendMsg = instruction + ' ' + senderID + '\n'
            for cID in clientele:
                clientele[cID].send(sendMsg.encode())
        elif instruction == 'brushEnd':
            sendMsg = instruction + ' ' + senderID + '\n'
            for cID in clientele:
                clientele[cID].send(sendMsg.encode())



        print()
        serverChannel.task_done()


clientele = dict()
playerNum = 0
strokes = list()
shapes = list()
images = list()
texts = list()
isMousePressed = False

serverChannel = Queue(100)
threading.Thread(target=serverThread, args=(clientele,
                                            serverChannel)).start()

names = ['Teacher']
names += ['Student' + str(i) for i in range(1, BACKLOG)]


while True:
    # runs on new client join

    (client, address) = server.accept()

    # myID is the key to the client in the clientele dictionary

    myID = names[playerNum]
    clientele[myID] = client
    client.send(('myIDis %s \n' % myID).encode())
    print('connection recieved from %s' % myID)
    for stroke in strokes:
        msg = "newStroke %s" % (myID)
        for point in stroke:
            msg += " "+str(point).replace(" ", "")
        msg += "\n"
        print("sent", msg)
        client.send(msg.encode())

    for shape in shapes:
        client.send(("spawnShape %s %s %f %f %f %f %s\n" % ("server",str(shape[0]),shape[1],shape[2],shape[3],shape[4],str(shape[5]))).encode())

    for image in images:
        client.send(("spawnImage %s %s %f %f\n" % ("server",str(image[0]),float(image[1]),float(image[2]))).encode())

    for text in texts:
        client.send(("text %s %f %f %s %s\n" % ("server",text[0],text[1],text[2],str((text[3])))).encode())

    threading.Thread(target=handleClient, args=(client, serverChannel,
                                                myID, clientele)).start()
    playerNum += 1