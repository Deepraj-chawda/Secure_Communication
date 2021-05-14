'''
client socket for communication
'''

# importing socket module for creating sockets
import socket
# importing json module for data serialization and deserialization
import json
# importing Thread from threading for concurrent programming
from threading import Thread
# import sleep from time module for delay functionality
from time import sleep
# importing sys module for system i/o
import sys
# importing hashlib module for hashing passcode
import hashlib
# importing cryptography module for encryting and decryting messages
from cryptography.fernet import Fernet


class Client:
    '''TCP Client socket according to Secure communication Protocols
    or client class
    '''

    def __init__(self, ip, port=8082):
        '''
        initializing server IP and Port

        :param ip: server IP Address
        :param port: Server Port
        '''

        self.server_ip = ip
        self.port = port
        self.local_port = port
        self.user_id = None
        self.client = None
        self.chat = False
        self.connect_to_server()

    def connect_to_server(self):
        '''
        Creating a client socket and
        connecting to server using server IP and Port
        :return: None
        '''

        # Creating a client socket
        # creating a TCP type and  IPV4 faimly Socket
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        # Connecting to Server
        self.client.connect((self.server_ip, self.port))
        print(f"Connected to server at {self.server_ip}")

    def processing_requests(self):
        '''
        processing different client requests according to predefine protocols
        :return: None
        '''

        # sending authentication request to server
        authentication_response = self.authentication_phase()

        # checking Status of authentication response
        if authentication_response['status'] == 'GRANTED':
            choice = input('Do you want to Begin chat with  other user (Y or N): ')

            if choice.upper() == 'Y':

                # Taking Lookup ID
                lookup_id = input('Enter destination user ID : ')
                # Sending lookup request to server
                lookup_response = self.lookup_phase(lookup_id)
                # Checking Status of Lookup response
                if lookup_response['status'] == 'SUCCESS':

                    # Request for connection phase
                    self.connection_phase(lookup_response)

                else:
                    print('Lookup status NOTFOUND')

            elif choice.upper() == 'N':
                # Receiving connection request
                self.connection_receive()

            else:
                print("Invalid input !!! (Y or N)")

        else:
            print('Authentication status REFUSED')

    def authentication_phase(self):
        '''
        sending authentication request to server according to predefine protocols
        :return: response from server
        '''
        # Salts for hashing passcode
        with open('users_key.json', 'r') as file:
            salts = json.load(file)
            file.close()

        # Taking User Id and Passcode
        self.user_id = input('Enter User ID : ')
        passcode = input('Enter passcode : ')

        # Hashing passcode using sha256 hashing algorithm
        my_salt = salts.get(self.user_id, ['', '00'])[1]
        passcode = hashlib.sha256((passcode + my_salt).encode()).hexdigest()

        # authentication request
        request = {
            "msgtype": "AUTHREQ",
            "userid": self.user_id,
            "passcode": passcode
        }

        # sending authentication request to server
        self.client.send(json.dumps(request).encode('utf-8'))

        # Receiving server Response
        response = json.loads(self.client.recv(2048).decode())

        # closing client socket
        self.client.close()
        self.client = None

        return response

    def lookup_phase(self, lookup_id):
        '''
        #Sending lookup request to server according to predefine protocols
        :param lookup_id: lookup id of user
        :return: response from the server
        '''
        # creating new client socket to connect with server
        self.connect_to_server()
        # Lookup request
        request = {
            "msgtype": "LOOKUPREQ",
            "userid": self.user_id,
            "lookup": lookup_id
        }

        # sending Lookup request to server
        self.client.send(json.dumps(request).encode('utf-8'))

        # Receiving lookup response
        response = json.loads(self.client.recv(2048).decode('utf-8'))

        # closing client socket
        self.client.close()
        self.client = None
        return response

    def connection_phase(self, lookup):
        '''
        Sending connection request to other client
        :param lookup: lookup response from server
        :return: None
        '''

        # for creating local client socket
        local_client = self.create_local_client(lookup)

        # Connection request
        request = {
            "msgtype": "CONNECTREQ",
            "initiator": self.user_id
        }

        # sending Connection request to local server
        local_client.send(json.dumps(request).encode('utf-8'))
        # closing local client socket
        local_client.close()

        # for creating local server socket
        local_server, client_local = self.create_local_server()

        # Receiving connection response from local client
        response = json.loads(client_local.recv(2048).decode('utf-8'))

        if response['status'] == 'ACCEPTED':
            # chatting phase
            self.chatting(client_local, lookup['encryptionkey'], lookup['answer'])
        else:
            print('Connection REFUSED')

        # closing local client and server
        client_local.close()
        local_server.close()

    def create_local_client(self, lookup):
        '''
        creating a local client socket
        :param lookup: lookup response from server
        :return: local_client socket
        '''
        try:
            # creating a TCP type and  IPV4 faimly Socket
            local_client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

            # local server IP and port
            local_server_ip = lookup['address']
            self.local_port += 1

            # Connecting to  local Server
            local_client.connect((local_server_ip, self.local_port))

            return local_client

        except ConnectionError:
            print('Failed to connect !!!...')
            # Exit program
            sys.exit(-1)

    def connection_receive(self):
        '''
         Receiving connection request from other client
        :return: None
        '''

        # reply of connection request
        reply = {
            "msgtype": "CONNECTREPLY",
            "status": "REFUSED"
        }

        # creating local server
        local_server, client_local = self.create_local_server()

        # Receiving  connection request from local client
        request = json.loads(client_local.recv(2048).decode('utf-8'))

        # closing local server and client
        client_local.close()
        local_server.close()

        # checking connection request
        if request['msgtype'] == 'CONNECTREQ':

            # lookup into server
            response = self.lookup_phase(request['initiator'])

            if response['status'] == 'SUCCESS':
                reply['status'] = 'ACCEPTED'

            else:
                print('Lookup status NOTFOUND')

            # creating local client
            local_client = self.create_local_client(response)

            # Replying connection response to local server
            local_client.send(json.dumps(reply).encode('utf-8'))

            if response['status'] == 'SUCCESS':
                # chatting phase
                self.chatting(local_client, response['encryptionkey'], request['initiator'])

            # closing local client socket
            local_client.close()

    def create_local_server(self):
        '''
        creating local server socket
        :return: local_server , client_local
        '''

        # creating a TCP type and  IPV4 faimly Socket
        local_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

        # local server IP and Port
        server_ip = ''
        self.local_port += 1

        # Binding local server
        local_server.bind((server_ip, self.local_port))

        # local server is ready to listen or accept clients request
        local_server.listen()

        # accepting client request
        client_local, _ = local_server.accept()

        return local_server, client_local

    def send_msg(self, client_, my_key):
        '''
        sending message to other client
        :param client_: client socket
        :param my_key: user encryption key
        :return: None
        '''

        # encrypting message using cryptography
        encrypt_msg = Fernet(my_key)

        while self.chat:
            try:
                message = input('\n')
                # encrypting message
                message = encrypt_msg.encrypt(message.encode())

                # sending message to other client
                client_.send(message)
                sleep(0.5)

            except ConnectionError:
                break
            except EOFError:
                break

        self.chat = False

    def receive_msg(self, client_, key, user_id):
        '''
        receiving message from other client
        :param client_: client socket
        :param key: user encryption key
        :param user_id: client user ID
        :return: None
        '''

        # decrypting message using cryptography
        decrypt_msg = Fernet(key)

        while self.chat:
            try:
                # Receiving message from other client
                message = client_.recv(1024)
                # decrypting message
                message = decrypt_msg.decrypt(message).decode('utf-8')

                # printing message
                print(f"{user_id}: {message}\n".rjust(100))
                sleep(0.5)

            except ConnectionError:
                break
            except EOFError:
                break

        self.chat = False

    def chatting(self, client_, key, other_user_id):
        '''
        chatting or communication between clients
        :param client_: client socket
        :param key: encryption key
        :param other_user_id:
        :return: None
        '''

        # start chatting
        self.chat = True
        print('\nStart chatting ..............\n')

        # opening a users_keys file
        with open('users_key.json') as file:
            # store encryption keys
            encrypt_keys = json.load(file)
            file.close()

        # creating thread of send function
        send_ = Thread(target=self.send_msg, args=(client_, encrypt_keys[self.user_id][0]))

        # creating thread of receive function
        receive = Thread(target=self.receive_msg, args=(client_, key, other_user_id))

        try:
            send_.daemon = True
            receive.daemon = True

            # starting both the thread
            send_.start()
            receive.start()

            send_.join()
            receive.join()

        except KeyboardInterrupt:
            pass

    def __del__(self):
        '''
        delete self
        :return: None
        '''

        del self


if __name__ == '__main__':

    if len(sys.argv) == 2:
        Server_IP = sys.argv[1]
    else:
        print("\nUsages: client.py server_IP_address")
        sys.exit(0)

    try:

        client = Client('127.0.0.1')
        # processing requests
        client.processing_requests()

    except KeyboardInterrupt:
        del client

    print('\n\nClosing client .....')
