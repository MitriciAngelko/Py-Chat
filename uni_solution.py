# import required modules
import socket
import threading

HOST = '143.47.184.219'
PORT = 5378

username = ""               # username global because we want to access it in multiple functions

def user_login(client):     # function that takes care of the user login part
    global username         # username is global and in python we need 'global' keyword to mention that                                                            
    username = input("Enter username: ")                    # asking the user for the username
    while(username == ""):                                  # we don't accept empty usernames
        print("Username cannot be empty!")                  # message for that
        username = input("Enter username: ")                # asking for another message
    
    message_to_server = "HELLO-FROM " + username + '\n'     # the protocol: the format message 
    client.send(message_to_server.encode("utf-8"))          # sends the message to the server from the client

    response_from_server = client.recv(4096).decode("utf-8")            # we receive the message from the server in variable 'response_from_server'

    # HELLO thing
    if(response_from_server == "HELLO " + username + '\n'):             # in order not to expose the protocol we print user friendly messages
        print("Successfully logged in!\n")
    
    # IN-USE thing
    if(response_from_server == "IN-USE\n"):                 # same here 
        print("ERROR! Username already in use! Try a different username!")
        user_login(client)                                  # if username already exists, we simply do the whole procedure again after printing a message

    # BUSY thing
    if(response_from_server == "BUSY\n"):
        print("ERROR! Server is too busy at the moment! Please try again later!")
 
def user_list(client):      # function that takes care of the !who command
    # LIST and LIST-OK thing
    message_to_server = "LIST" + '\n'                               # the protocol: the format message
    client.send(message_to_server.encode("utf-8"))                  # send the message to the server from the client

    message_from_server = ""                                        # we start with an empty message
    while True:                                                     # as long as we have parts of the message to read we stay in the loop
        temporary_message = client.recv(4096).decode("utf-8")                       # we receive at max 4096 bytes and store them in the temporary_message
        if not temporary_message:                                   # if there is nothing more to receive we break out of the loop
            break
        message_from_server = message_from_server + temporary_message           # we add parts of the message to form the whole message

    decoded_message = message_from_server.decode("utf-8")                       # in this variable we will have the full message decoded
    print("Currently logged-in users: ")
    print(decoded_message[8:])                                 # we print from character 8(that's what 8: does) because the first part is only protocol message

def user_message(client, input_command):
    print(input_command)

def send_messages(client):
    global username
    while True:
        input_command = input('@' + username + ": ")
        if (input_command == "!quit"):
            print("Successfully logged out!")
            break
        elif (input_command == "!who"):
            user_list(client)
        elif (input_command.startswith('@')):
            user_message(client, input_command)
        else:
            print("ERROR! Invalid command!")

# receive messages function
def receive_messages(client):
    while True:                 # we listen continuously in for messages from server              
        message_from_server = ""                # we start an empty message 
        entry_1 = True
        while True:
            temporary_message = client.recv(4096).decode("utf-8")       # we can receive up to 4096 bytes at a time
            if(temporary_message == "" and entry_1 == True):
                continue
            entry_1 = False
            if not temporary_message:                   # if we have no more parts of the message to receive we get out of loop
                break
            message_from_server = message_from_server + temporary_message           # we construct the whole message here 
        entry_1 = False
        decoded_message = message_from_server
        sender_username = decoded_message.split()[1]       # split separated the words and we only need the second word and we store it into 'sender_username'
        sender_message = " ".join(decoded_message.split[2:])     # we need the rest of the string so we store from the 3rd word (2: does that for us)
        message_to_print = '@' + sender_username + ": " + sender_message
        print(message_to_print)

# main function
def main():
    # creating a socket object on the client side
    # AF_INET = argument that says we are going to use IPv4 addresses
    # SOCK_STREAM = argument that says we are using TCP packets for communication
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the server
    try:
        client.connect((HOST, PORT))
        # message to be sure we connected
        print("Successfully connected to server")
    except:
        print(f"Unable to connect to server {HOST} {PORT}")

    user_login(client)
    
    # start a new thread to send messages
    send_thread = threading.Thread(target=send_messages, args=(client, ))
    send_thread.start()
    
    # start a new thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client, ))
    receive_thread.start()

    
    
if __name__ == "__main__":
    main()