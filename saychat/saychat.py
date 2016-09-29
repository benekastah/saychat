import random
import re
import select
import socket
import subprocess
import sys


def get_voices():
    result = subprocess.check_output(['say', '-v', '?'])
    voices = []
    for line in result.decode().splitlines():
        match = re.search(r'^(?P<name>[\w-]+(\s[\w-]+)*)\s+(?P<locale>[\w-]+)\s+#.*$', line)
        if not match:
            print('No match: ', line)
            continue
        name, locale = match.group('name'), match.group('locale')
        if locale.startswith('en_') or locale.startswith('en-'):
            voices.append(name)
    return voices


VOICES = get_voices()
voices_by_ident = {}


def get_voice(ident):
    global voices_by_ident
    if ident not in voices_by_ident:
        used_voices = set(voices_by_ident.values())
        for _ in range(len(VOICES)):
            voice = random.choice(VOICES)
            voices_by_ident[ident] = voice
            if voice not in used_voices:
                break
    return voices_by_ident[ident]


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
                    ident, message = data.decode().split('\t', maxsplit=1)

                    match = re.search(r'^\\voice\s+(?P<voice>.+)', message, re.IGNORECASE)
                    if match:
                        voice = match.group('voice')
                        if voice in VOICES:
                            voices_by_ident[ident] = voice
                        continue

                    say(message, get_voice(ident))
            else:
                # user entered a message
                msg = sys.stdin.readline()
                s.send(msg.encode())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python saychat.py hostname port')
        sys.exit()
    chat_client(sys.argv[1], int(sys.argv[2]))
