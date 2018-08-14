# Virtual Classroom
My Carnegie Mellon 15-112 Term Project (M18)

## Description & Purpose: 
My virtual classroom project intends to serve the vast community of academia by providing a platform in which teachers and students alike can share ideas not only in the confines of a physical classroom. A virtual classroom allows two or more participants to communicate and collaborate in a class-like environment to simulate an actual classroom but with much more convenience and access to learning tools. Such learning tools include the ability to collaborate via a whiteboard using Sockets and Tkinter in Python 3. In the future, I hope to add additional functionality such as an option for audio and/or video chat, and an option to upload and download files through the classroom.

## Getting Started
The following instructions will explain how to get all of the necessary components of the virtual classroom to run on your local machine. 

### Installing Dependencies
Assure you have the following modules installed to assure a working virtual classroom:

```
Python 3.6
Tkinterface
Math
Socket
Threading
Queue
```

### Starting the server (Locally)

In the virt-class-server.py file, assure that the line starting with HOST is as follows: "HOST = '127.0.0.1'" This will allow the server to connect using your local network. Next, start the server by running it in your favorite IDE or using terminal.

```
clear;python3 virt-class-server.py
```

### Starting the client (Locally)

In the virt-class-client.py file, assure that the line starting with HOST is as follows: "HOST = '127.0.0.1'" This will assure that the client connects to the same network as the server. Now, start the client using your favorite IDE or using terminal. Assure you are using a new terminal window when using the program locally.

```
clear;python3 virt-class-client.py
```

## Expansion Plans

Following the conclusion of the course, I wish to expand this program to be open source and to be edited by fellow programmers with the same purpose in mind. Furthermore, I hope that I can eventually use this project to allow programmers to teach individuals in economically disadvanted areas and set-up a platform that will connect these two parties.
