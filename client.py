import socket
import threading
import sys
import os
from pathlib import Path
# Ensure the correct number of arguments are provided
if len(sys.argv) < 4:
    print("Incorrect number of inputs <python client.py [username] [hostname] [port]>")
    sys.exit(1)
# Ensure the port number is an integer
if sys.argv[3].isdigit() == False: 
    print("Port number must be an integer")
    sys.exit(1)
NAME = sys.argv[1]
HOST = sys.argv[2]
PORT = int(sys.argv[3])
CLIENT_SHARED_FILES = os.path.join(os.path.dirname(__file__), NAME)

# Function to receive a file from the server
def receive_file(client_socket): 
    p = Path(NAME)
    p.mkdir(exist_ok=True)
    metadata = client_socket.recv(1024)
    print(f"Raw metadata received: {metadata}")
    try:
        metadata = metadata.decode().strip()
        if not metadata:
            print("Metadata not received")
            return
        file_name, file_size = metadata.split(":")
        file_size = int(file_size)
        file_name = file_name[13:]
        print(f"Receiving file: {file_name} ({file_size} bytes)")
        file_path = p / file_name
        # Receive the file data and writes it to the local folder with the users name
        with open(file_path, "wb") as file:
            while file_size > 0:
                chunk = client_socket.recv(min(file_size, 4096))
                if not chunk:
                    break
                file.write(chunk)
                file_size -= len(chunk)
        print(f"File {file_name} received successfully.")
        print("Enter message: ")
    except UnicodeDecodeError as e:
        print(f"Error decoding metadata: {e}")
    except Exception as e:
        print(f"Error receiving file: {e}")

#This code defines the function list_client_files() that lists the files in the client's personal named directory.

def list_client_files():
    try:
        if not os.path.exists(CLIENT_SHARED_FILES):
            print(f"Shared files directory '{CLIENT_SHARED_FILES}' does not exist.")
            return
        files = [file for file in os.listdir(CLIENT_SHARED_FILES) if os.path.isfile(os.path.join(CLIENT_SHARED_FILES, file))]
        for file in files:
            print(file + " " + os.path.getsize(os.path.join(CLIENT_SHARED_FILES, file)) + " bytes")
    except Exception as e:
        print(f"Error listing client files: {e}")

#This code utilises threading to continuously receive messages or file transfers from the server and handle them accordingly
#
def receive_messages(client_socket, stop_event):
    while not stop_event.is_set():
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Connection closed by the server.")
                break
            if message.startswith("File incoming"):
                receive_file(client_socket)
            else:
                print(f"\n{message}")
        except socket.error as e:
            if not stop_event.is_set():
                print(f"Error receiving message: {e}")
            break
    client_socket.close()



def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stop_event = threading.Event()
    try:
        client_socket.connect((HOST, PORT))
        print("Connected to the server!")
        client_socket.send(NAME.encode())
        
        welcome_message = client_socket.recv(1024).decode()
        print(welcome_message)
    
        receiver_thread = threading.Thread(target=receive_messages, args=(client_socket, stop_event))
        receiver_thread.start()

        while True:
            message = input("Enter message: ")
            if message.lower() == 'exit':
                print("Disconnecting...")
                stop_event.set() # Tells the reciver thread to stop running as the user wants to exit
                client_socket.send("exit".encode())
                break
            elif message.lower() == 'list client files':
                list_client_files()
            elif message.startswith("download"):
                client_socket.send(message.encode())
            else:
                client_socket.send(message.encode())
            
    except ConnectionRefusedError:
        print("Unable to connect to the server. Is it running?")
    except KeyboardInterrupt:
        print("\nInterrupted. Disconnecting...")
        stop_event.set()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        stop_event.set()  # Tells the reciver thread to stop running as the user is exiting due to an error
        client_socket.close()
        print("Disconnected from the server.")

if __name__ == "__main__":
    main()
