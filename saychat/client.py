import select
import socket
import subprocess
import sys


def prompt():
    sys.stdout.write('> ')
    sys.stdout.flush()


def say(message, voice=None):
    args = ['say', message]
    if voice:
        args += ['-v', voice]
    subprocess.call(args)


def chat_client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try:
        s.connect((host, port))
    except OSError:
        print('Unable to connect')
        sys.exit()

    print('Connected to remote host. You can start sending messages')
    prompt()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(4096)
                if not data:
                    print('\nDisconnected from chat server')
                    sys.exit()
                else:
                    sys.stdout.write(data.decode())
                    prompt()
            else:
                # user entered a message
                msg = sys.stdin.readline()
                s.send(msg.encode())
                prompt()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python saychat.py hostname port')
        sys.exit()
    chat_client(sys.argv[1], int(sys.argv[2]))
