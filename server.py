import socket
import threading
import sys
import os

#This code declares constants and environment variables that will be used in the server.py file.
SERVER_SHARED_FILES = os.path.join(os.path.dirname(__file__), "SharedFiles")
HOST = '127.0.0.1'
PORT = int(sys.argv[1])
clients = []
users = {}
lock = threading.Lock()


#This code defines the function send_file(client_socket, file_name) that sends a file to a client.

def send_file(client_socket, file_name):
    with lock:
        file_path = os.path.join(SERVER_SHARED_FILES, file_name)
        if not os.path.exists(file_path):
            client_socket.send("Error- file does not exist.\n".encode())
            return
        try:
            file_size = os.path.getsize(file_path)
            client_socket.send("File incoming".encode())
            client_socket.send(f"{file_name}:{file_size}\n".encode())
            with open(file_path, "rb") as file:
                while chunk := file.read(4096):
                    client_socket.sendall(chunk)
            
            print(f"File '{file_name}' sent successfully.")
        except Exception as e:
            print(f"Error sending file '{file_name}': {e}")
            client_socket.send("Error- unable to send file.\n".encode())


#This code defines the function access_server_files(client_socket) that sends a message to a client with the number of files in the SharedFiles directory on the server.
#It also ensures the client has access to the SharedFiles directory before attempting to download or list any files.
def access_server_files(client_socket):
    with lock:
        try:
            files = [file for file in os.listdir(SERVER_SHARED_FILES) if os.path.isfile(os.path.join(SERVER_SHARED_FILES, file))]
            response = f"You have sucessfull accessed the SharedFiles on the server \nThe number of files in SharedFiles is {len(files)}\n" + ("Enter message: ")
            client_socket.sendall(response.encode())
        except Exception as e:
            print(f"Error accessing files: {e}")
            client_socket.send("Error -unable to access files.\n".encode())
            client_socket.send("Enter message: ".encode())

#This code defines the function list_server_files(client_socket) that sends a message to a client with the list of files in the SharedFiles directory on the server.

def list_server_files(client_socket):
    with lock:
        try:
            files = [file for file in os.listdir(SERVER_SHARED_FILES) if os.path.isfile(os.path.join(SERVER_SHARED_FILES, file))]
            response = f"\n".join(files) + "\n" + ("Enter message: ")
            client_socket.sendall(response.encode())
        except Exception as e:
            print(f"Error listing files: {e}")
            client_socket.send("Error - unable to list files.\n".encode())
            client_socket.send("Enter message: ".encode())


#This code broadcasts a message to all clients except the sender.

def broadcast_message(message, sender_socket):
    with lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    clients.remove(client)

#This code sends a private message to a specific client.
def unicast_message(message, recipient_name):
    with lock:
        if recipient_name in users:
            try:
                users[recipient_name].send(message.encode())
            except Exception as e:
                print(f"Failed to send message to {recipient_name}: {e}")
                del users[recipient_name]
        else:
            print(f"User {recipient_name} not found.")
#This code defines the function handle_client(client_socket, address) that handles a client connection.
#It is the code that is initated when a new thread begins, ensuring that the server can handle multiple clients simultaneously.

def handle_client(client_socket, address):
    name = None
    files_opened = False
    try:
        name = client_socket.recv(1024).decode().strip()
        if not name:
            client_socket.send("Error- name cannot be empty.\n".encode())
            return

        
        print(f"New connection from {name} at {address}")
        welcome_message = f"Welcome to the server, {name}!"
        client_socket.sendall(welcome_message.encode())
        broadcast_message(f"{name} has joined the chat".encode(), client_socket)
        broadcast_message(f"Enter message: ".encode(), client_socket)

        with lock:
            clients.append(client_socket)
            users[name] = client_socket
        
        while True:
            message = client_socket.recv(1024)
            # If the message is empty, the client has disconnected
            #Below are the range of commands a client might send to the server, prompting the server to
            #list files, access files, download files, send private messages or exit the chat.
            if not message:
                break
            
            if message == "exit": #exit command
                print(f"{name} has left")
                break
            
            message = message.decode('utf-8').strip()
            
            if message.startswith("@"): #unicast command
                parts = message.split(" ", 1)
                if len(parts) < 2:
                    client_socket.send("Error- invalid private message format. Use @name message.\n".encode())
                    continue
                recipient_name, private_message = parts[0][1:], parts[1]
                unicast_message(f"Private from {name}: {private_message}", recipient_name)
            
            elif message == "list server files": #list server files command
                if not files_opened:
                    client_socket.send("Error- access server files first.\n".encode())
                else:
                    list_server_files(client_socket)
            
            elif message == "access server files": #enables access to server files
                files_opened = True
                access_server_files(client_socket)
            
            elif message.startswith("download"): #command prompt to download files
                if not files_opened:
                    client_socket.send("Error- access server files first.\n".encode())
                else:
                    client_socket.send("File incoming".encode())
                    message_parts = message.split(" ", 1)
                    send_file(client_socket, message_parts[1])
                
            else:
                print(f"Message from {name}: {message}") #broadcasts message to all clients
                broadcast_message(f"{name}: {message}\n".encode(), client_socket)

    except Exception as e:
        print(f"Error with client {address}: {e}")
    finally:
        broadcast_message(f"{name} has left the chat\n".encode(), client_socket)
        print(f"Connection closed for {address}")
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
            if name in users:
                del users[name]
        client_socket.close()
#This is the main function that creates new server sockets for each client that attempts to connect to the server
#It then initialises each thread to handle the client connection.
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server running on {HOST}:{PORT}")
    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Accepted connection from {address}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("Closing server...") #This code ensures that the server can be shut down gracefully.
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
