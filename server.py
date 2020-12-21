import socket

PORT = 3000
IP_ADDRESS = "127.0.0.1"
from threading import Thread

USERS_LIST = {}
SOCKET_LIST = {}
thread = None

NEW_USER_MESSAGE_TYPE = 'NEWUSER'
LOGOUT_MESSAGE_TYPE= 'LOGOUT'
BROADCAST_MESSAGE_TYPE= 'BROADCAST'


def main():
    global thread
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # open socket with adress family IPv4, use TCP
    sock.bind((IP_ADDRESS, PORT))  # Binds the socket to address
    print('Listening on Port ', PORT, ' for incoming TCP connections')
    sock.listen()
    while True:
        try:
            conn, addr = sock.accept()
            print('Incoming connection accepted: ', addr)
            nickname = conn.recv(1028).decode()
            register_user(nickname, addr, conn)

            # start thread to listen to every user messages
            t = Thread(target=listen, kwargs={'nickname': nickname})
            thread = t
            t.start()
            
        except socket.timeout:
            print('Socket timed out listening')


def handle_message(data, nick):
    command, message = data.split('_')
    if command == BROADCAST_MESSAGE_TYPE:
        data_to_send = (nick, message)
        send_message_to_all(BROADCAST_MESSAGE_TYPE + '_' + str(data_to_send))
    if command == LOGOUT_MESSAGE_TYPE:
        USERS_LIST.pop(nick)
        SOCKET_LIST.pop(nick)
        send_message_to_all(LOGOUT_MESSAGE_TYPE + '_' + nick)

def send_message_to_all (message):
    for nickname, conn in SOCKET_LIST.items():
        conn.send(message.encode())

def listen(nickname):
    while True:
        message = SOCKET_LIST[nickname].recv(1028)
        handle_message(message.decode(), nickname)
        command, message = message.decode().split('_')
        if command == LOGOUT_MESSAGE_TYPE:
            print("koko")
            break

def register_user(nickname, addr, conn):
    USERS_LIST[nickname] = addr
    broadcast(nickname, addr)
    SOCKET_LIST[nickname] = conn
    conn.send(str(USERS_LIST).encode())

def broadcast(nick, addr):
    for nickname, conn in SOCKET_LIST.items():
        conn.send(new_user_message(nick, addr))


def new_user_message(nickname, addr):
    return (NEW_USER_MESSAGE_TYPE + '_' + str((nickname, addr))).encode()


if __name__ == '__main__':
    main()
