import socket
import ast
from threading import Thread
import sys

PORT = 3000
IP_ADDRESS = "127.0.0.1"

USERS_LIST = {}
threads = []

NEW_USER_MESSAGE_TYPE = 'NEWUSER'
LOGOUT_MESSAGE_TYPE = 'LOGOUT'
BROADCAST_MESSAGE_TYPE = 'BROADCAST'


# open socket with adress family IPv4, use TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def decode_list_of_users(data):
    global USERS_LIST
    USERS_LIST = ast.literal_eval(data.decode())
    print("\nList of Users defined\n")
    print("User's: " + str(USERS_LIST))


def update_notification(data):
    command, message = data.split('_')
    if command == NEW_USER_MESSAGE_TYPE:
        nickname, addr = ast.literal_eval(message)
        USERS_LIST[nickname] = addr
        print("\nList of Users updated\n")
    if command == BROADCAST_MESSAGE_TYPE:
        nickname, chat_msg = ast.literal_eval(message)
        print(nickname + ': ' + chat_msg)
    if command == LOGOUT_MESSAGE_TYPE:
        USERS_LIST.pop(message)
        print("\nUser has left: " + message + '\n')

#BOLD + UNDERLINE


def main():
    global threads
    sock.connect((IP_ADDRESS, PORT))
    nickname = input("Please provide a nickname: ")
    sock.send(nickname.encode())
    data = sock.recv(1024)
    decode_list_of_users(data)

    t = Thread(target=listen_to_update)
    threads.append(t)
    t.start()

    i = Thread(target=process_user_input)
    threads.append(i)
    i.start()

    for thread in threads:
        thread.join()


def process_user_input():
    command = input('Enter command: ').lower()
    print('use <b> for Broadcast \n use <m> for massege to a user \n use <q> for quit \n')
    while True:             # TODO: muss auch aus schleife rausspringen um andere optionen wählen zu können
        if command == "b":
            message = input('Message to broadcast: \n')
            sock.send((BROADCAST_MESSAGE_TYPE + '_' + message).encode())
            command = input('Enter command: ').lower()
        # if command == "m":
        #     print("as")
        #     toUser = input('User for Message: \n')
        #     message = input('Message to ' + toUser + ': \n').lower()
        if command == "q":
            logout()
        else:
            print(
                'use <b> for Broadcast \n use <m> for massege to a user \n use <q> for quit')


def listen_to_update():
    while True:
        data = sock.recv(1024)
        update_notification(data.decode())


def logout():
    print("Quitting ...")
    sock.send((LOGOUT_MESSAGE_TYPE + '_').encode())

    for thread in threads:
        if not thread.is_alive():
            threads.remove(thread)
            thread.join()

    sock.close()
    sys.exit()


if __name__ == '__main__':
    main()
