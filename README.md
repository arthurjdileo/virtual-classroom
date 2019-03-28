# Virtual Classroom
My Carnegie Mellon [15-112](http://www.cs.cmu.edu/~112n18/) Term Project (N18)

## Description & Purpose: 
My virtual classroom project intends to serve the vast community of academia by providing a platform in which teachers and students alike can share ideas not only in the confines of a physical classroom. A virtual classroom allows two or more participants to communicate and collaborate in a class-like environment to simulate an actual classroom but with much more convenience and access to learning tools. Such learning tools include the ability to collaborate via a whiteboard using Sockets and Tkinterface in Python 3. In the future, I hope to add additional functionality such as an option for audio and/or video chat, and an option to upload and download files through the classroom.

## Getting Started
The following instructions will explain how to get all of the necessary components of the virtual classroom to run on your local machine. 

### Installing Dependencies
Assure you have the following modules installed to assure a working virtual classroom:

```
Python 3.6
flask
slackclient
datetime
apscheduler
pytz
```

### Starting the bot

In the bot.py file, you can find the channel ID that it will post updates to as well as notification intervals that you can set. Also make sure to set your environment variable in the environment file with your Bot User OAuth Access Token.

```
clear;python3 bot.py
```

### Docker

I also included the Dockerfile setup so that if you want you can move it to a Kubernetes platform or similar. If you plan to just use docker, the JSON file is already mounted for you. However, if you move to a Kubernetes platform, you must ensure you account for persistance with the JSON file. I am planning to move to Google Datastore for v2.

```
clear;python3 run_docker.py
```
