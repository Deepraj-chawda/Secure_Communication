'''
server socket for communication
'''

# importing socket module for creating sockets
import socket
# importing json module for data serialization and deserialization
import json
# importing sys module for system i/o
import sys


class Server:
    '''
     TCP IP server to accept and process client requests according to super
      secure communication protocols.
    '''

    def __init__(self, ip, port=8082):
        '''
        initializing server IP and Port
        :param ip: server IP Address
        :param port: Server Port
        '''
        self.online_users = {}
        self.server_ip = ip
        self.server_port = port
        self.server = None
        self.client_socket = None
        self.client_ip = None
        self.initialize_server_socket()

    def initialize_server_socket(self):
        '''
        Creating A server Socket using Server IP and Port
        :return: None
        '''

        # creating a TCP type and  IPV4 faimly Socket
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

        # Binding server to server IP and Port
        self.server.bind((self.server_ip, self.server_port))

        # server is ready to listen or accept clients request
        self.server.listen()

    def logged_in(self):
        '''
        it accept the client request and login to the system
        :return: None
        '''

        # accepting client request
        self.client_socket, (self.client_ip, _) = self.server.accept()

        # processing the request of client
        self.processing_requests()

        # closing client socket
        self.client_socket.close()

    def processing_requests(self):
        '''
        processing different client requests according to predefine protocols
        :return: None
        '''

        # Receiving client request
        request = json.loads(self.client_socket.recv(2048).decode('utf-8'))

        if request['msgtype'] == 'AUTHREQ':
            # processing authentication request
            self.authentication_phase(request)

        elif request['msgtype'] == 'LOOKUPREQ':
            # processing Lookup request
            self.lookup_phase(request)

    def authentication_phase(self, request):
        '''
        Authentication phase according to predefine protocols
        :param request: request of client
        :return: None
        '''

        # creating  Authentication reply message
        reply = {'msgtype': 'AUTHREPLY', 'status': 'REFUSED'}

        # loading data of all users from data base
        with open('data_base.json') as file:
            users = json.load(file)
            file.close()

        # Checking user Id in database
        if request['userid'] in users:
            # Checking passcode of user
            if request['passcode'] == users[request['userid']][0]:
                # Changing status to GRANTED
                reply['status'] = 'GRANTED'
                # Store user ID , IP Address and encryption key
                self.online_users[request['userid']] = [self.client_ip, users[request['userid']][1]]

        # Replying Authentication message
        self.client_socket.send(json.dumps(reply).encode())

    def lookup_phase(self, request):
        '''
         Lookup phase according to predefine protocols
        :param request: request of client
        :return: None
        '''

        # creating Lookup Reply message
        reply = {
            'msgtype': 'LOOKUPREPLY',
            'status': 'NOTFOUND',
            'answer': '',
            'address': '',
            'encryptionkey': ''
        }

        # checking both user id in online_users
        if request['userid'] in self.online_users and request['lookup'] in self.online_users:

            # Formating Lookup Reply message
            reply['status'] = 'SUCCESS'
            reply['answer'] = request['lookup']
            reply['address'] = self.online_users[request['lookup']][0]
            reply['encryptionkey'] = self.online_users[request['lookup']][1]

        # Replying Lookup phase message
        self.client_socket.send(json.dumps(reply).encode('utf-8'))

    def __del__(self):
        '''
        closing server sockect
        :return: None
        '''

        self.server.close()


if __name__ == '__main__':

    if len(sys.argv) == 2:
        server_ip = sys.argv[1]
    else:
        print("Usages: client.py server_IP_address")
        sys.exit(0)

    try:
        server = Server(server_ip)
        print(f"Server is Running at {server.server_ip} and port {server.server_port}")
        while True:
            # Accepting client Request
            server.logged_in()

    except KeyboardInterrupt:
        del server
        print("Closing Server .....")
