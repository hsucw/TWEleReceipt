import socket, ssl
import threading

bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bindsocket.bind(('', 10443))
bindsocket.listen(5)

def deal_with_client(connstream):
    data = connstream.read()
    while data:
        print "_"+data
        data = connstream.read()

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket,
                                 server_side=True,
                                 certfile="cert/server.crt",
                                 keyfile="cert/server.key",
                                 ssl_version=ssl.PROTOCOL_SSLv23)
    try:
        deal_with_client(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()
