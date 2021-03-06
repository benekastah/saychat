import select
import socket
import sys

SOCKET_LIST = []
RECV_BUFFER = 4096


def chat_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(10)

    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)

    print("Chat server started on port " + str(port))

    while 1:
        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0: poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print("Client (%s, %s) connected" % addr)

                broadcast(server_socket, sockfd, "Here I am!\n")

            # a message from a client, not a new connection
            else:
                # process data recieved from client,
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        broadcast(server_socket, sock, data.decode())
                    else:
                        # remove the socket that's broken
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "I went offline\n")

                # exception
                except OSError:
                    broadcast(server_socket, sock, "I went offline\n")
                    continue

    server_socket.close()


# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket:
            try:
                socket.send(b'%s\t%s' % (str(sock.getpeername()).encode(), message.encode()))
            except OSError:
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python saychat_server.py hostname port')
        sys.exit()
    chat_server(sys.argv[1], int(sys.argv[2]))
