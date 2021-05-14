'''
creating simple data base
'''

# importing json module
import json
# importing hashlib module
import hashlib
# importing sample from random for creating salt
from random import sample
# importing cryptography module
from cryptography.fernet import Fernet


def create_db(user_no=1):
    '''
    add user in data base
    :param user_no: no. of user added
    :return: None
    '''
    with open('data_base.json', 'r') as file:
        try:
            database = json.load(file)
        except json.JSONDecodeError:
            database = {}
        file.close()

    with open('users_key.json', 'r') as key_file:
        try:
            keys = json.load(key_file)
        except json.JSONDecodeError:
            keys = {}
        key_file.close()

    # Opening data base file in write mode
    with open('data_base.json', 'w') as file:

        with open('users_key.json', 'w') as key_file:

            for _ in range(user_no):
                # Taking user ID and passcode
                user_id = input('User ID : ')
                passcode = input('Passcode : ')
                # salt for hashing passcode
                salt = ''.join(sample('abcdef', 2))
                # Hashing passcode using sha256 hashing algorithm
                passcode = hashlib.sha256((passcode+salt).encode()).hexdigest()

                # Generating encryption key
                key = Fernet.generate_key().decode()

                database[user_id] = [passcode, key]
                keys[user_id] = [key, salt]

            json.dump(database, file)
            json.dump(keys, key_file)

            key_file.close()

        file.close()


if __name__ == '__main__':

    users = int(input("Enter the no. of user to be added : "))
    create_db(users)
