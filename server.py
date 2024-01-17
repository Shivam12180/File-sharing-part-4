import socket
from  threading import Thread
import time
import os 

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


IP_ADDRESS = '127.0.0.1'
PORT = 8010
SERVER = None
BUFFER_SIZE = 4096

clients = {}
def sendTextMessage(client_name,message):
    global clients
    other_client_name = clients[client_name]["connected_with"]
    other_client_socket = clients[other_client_name]["client"]
    final_message = client_name+" -> "+message
    other_client_socket.send(final_message.encode())

def handleErrorMessage(client):
    message='''You Need To Connect With One Of The Client First Before Sending Any Message. Click On Refresh To See All Available Users '''
    client.send (message.encode())

def disconnectWithClient(message,client,client_name):
    global clients
    enteredClientName = message[11:].strip()
    if (enteredClientName in clients):
        clients[enteredClientName]["connected_with"]=""
        clients[client_name]["connected_with"]=""

        otherClientSocket = clients[enteredClientName]["client"]
        greet_message = f"hello, {enteredClientName} you are successfully disconnected with {client_name} "
        otherClientSocket.send(greet_message.encode())

        msg = f"you are successfully disconnected with {enteredClientName}"
        client.send(msg.encode())

def handleClientConnection(message,client,client_name):
    global clients 
    enteredClientName = message[8:].strip()
    if (enteredClientName in clients):
        if (not clients[client_name]["connected_with"]):
            clients[enteredClientName]["connected_with"]=client_name
            clients[client_name]["connected_with"]=enteredClientName
            otherClientSocket = clients[enteredClientName]["client"]
            greet_message = f"hello, {enteredClientName} {client_name} connected with you "
            otherClientSocket.send(greet_message.encode())
            msg = f"you are successfully connected with {enteredClientName}"
            client.send(msg.encode())

        else:
            otherClientName = clients[client_name]["connected_with"]
            msg = f"you are already connected with {otherClientName}"
            client.send(msg.encode())


def handleShowList(client):
    global clients

    counter = 0
    for c in clients:
        counter +=1
        client_address = clients[c]["address"][0]
        connected_with = clients[c]["connected_with"]
        message =""
        if(connected_with):
            message = f"{counter},{c},{client_address}, connected with {connected_with},tiul,\n"
        else:
            message = f"{counter},{c},{client_address}, Available,tiul,\n"
        client.send(message.encode())
        time.sleep(1)


# Boilerlate Code
def handleMessges(client, message, client_name):
    if(message == 'show list'):
        handleShowList(client)

    elif(message[:7]=="connect"):
        handleClientConnection(message,client,client_name)
    elif(message[:10]=="disconnect"):
        disconnectWithClient(message,client,client_name)
    else:
        connected = clients[client_name]["connected_with"]
        if (connected):
            sendTextMessage(client_name,message)
        else:
            handleErrorMessage(client)

    


# Bolierplate Code
def handleClient(client, client_name):
    global clients
    global BUFFER_SIZE
    global SERVER

    # Sending welcome message
    banner1 = "Welcome, You are now connected to Server!\nClick on Refresh to see all available users.\nSelect the user and click on Connect to start chatting."
    client.send(banner1.encode())

    while True:
        try:
            BUFFER_SIZE = clients[client_name]["file_size"]
            chunk = client.recv(BUFFER_SIZE)
            message = chunk.decode().strip().lower()
            if(message):
                handleMessges(client, message, client_name)
            
        except:
            pass


# Boilerplate Code
def acceptConnections():
    global SERVER
    global clients

    while True:
        client, addr = SERVER.accept()

        client_name = client.recv(4096).decode().lower()
        clients[client_name] = {
                "client"         : client,
                "address"        : addr,
                "connected_with" : "",
                "file_name"      : "",
                "file_size"      : 4096
            }

        print(f"Connection established with {client_name} : {addr}")

        thread = Thread(target = handleClient, args=(client,client_name,))
        thread.start()


def setup():
    print("\n\t\t\t\t\t\tIP MESSENGER\n")

    # Getting global values
    global PORT
    global IP_ADDRESS
    global SERVER


    SERVER  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((IP_ADDRESS, PORT))

    # Listening incomming connections
    SERVER.listen(100)

    print("\t\t\t\tSERVER IS WAITING FOR INCOMMING CONNECTIONS...")
    print("\n")

    acceptConnections()

def ftp():
    global IP_ADDRESS
    authorizer = DummyAuthorizer()
    authorizer.add_user("lftpd","lftpd",".",perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    ftp_server= FTPServer((IP_ADDRESS,21),handler)
    ftp_server.serve_forever()





setup_thread = Thread(target=setup)           #receiving multiple messages
setup_thread.start()

ftp_thread = Thread(target = ftp)
ftp_thread.start