# Chatroom Client-Server Program

## Overview
This is a simple chatroom programme that runs a server and allows multiple clients to broadcast and unicast messages
You can also download files from the "SharedFiles" part of the server and store them to your personal local client files

## Requirements
- Python 3.x
- Network connectivity between client and server

## Setup
1. Clone the repository or download the source code.
2. Navigate to the project directory.

## Running the Server
1. Open a terminal window.
2. Navigate to the directory containing the server script.
3. Run the server script:
    ```
    python server.py [port]
    ```
4. The server will start and listen for incoming connections on the specified port.

## Running a new client
1. Open a terminal window.
2. Navigate to the directory containing the client script.
3. Run the client script with your username, hostname and port number:
    ```
    python client.py [username] [hostname] [port]
    ```
4. The client will connect to the server and send requests.

## Broadcasting a messages
To send a message to all clients on the chatroom, simply type your message and press enter

## Unicasting a messages
To send a message to a specified clients on the chatroom, type '@' followed by their name and then your message
to send a private message, for example
    ```
    @John Hello, how are you?
    ```


## Accessing server files
In order to download and list server files, you must first run the command to acess said files
Using 'access server files', providing the number of files in the server


## Listing server files
To find the names of the files in the server after accessing the server, use the the command 'list server files'

## Downloading server files
In order to download a file off of the server and store it in a local folder with your name, use the command 'download [filename]' 
where [filename] is the name of your file, including its extension, for example:
    ```
    download image1.png
    ```
The file will appear under your name directory


## Leaving the server
If the client want to leave the chatroom, they can use the command 'exit' to leave


## Configuration
- The server and client scripts can be configured by modifying the `HOST` and `PORT` variables in the respective scripts.

.

## Troubleshooting
- Issues downloading and listing file servers may be caused by not initiating accessing the files
- Ensure that the server is running before starting the client.
- Check network connectivity between the client and server.
- Verify that the `HOST` and `PORT` settings match in both the client and server scripts.
