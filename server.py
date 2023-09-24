import socket
import random
import string
from threading import Thread
import os
import shutil
from pathlib import Path


def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """
    dirs = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token():
    """Helper method to generates a random token that starts with '<' and ends with '>'.
     The total length of the token (including '<' and '>') should be 10.
     Examples: '<1f56xc5d>', '<KfOVnVMV>'
     return: the generated token.
     """
    pattern = string.ascii_letters + string.digits
    token = "<" + ''.join(random.choice(pattern) for i in range(8)) + ">"
    return token


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in client.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    data = bytearray()
    eof_token_consider = eof_token
    while True:
        packet = active_socket.recv(buffer_size)
        data.extend(packet)
        if packet[-10:] == eof_token_consider.encode():
            data = data[:-10]
            break

    return data


def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable 
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """

    if new_working_directory == "..":
        working_directory = os.path.dirname(current_working_directory)

    elif new_working_directory == ".":
        working_directory = current_working_directory

    else:
        working_directory = os.path.join(current_working_directory, new_working_directory)

    if os.path.exists(working_directory):
        return working_directory

    else:
        return current_working_directory


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    current_working_directory = current_working_directory

    path = os.path.join(current_working_directory, directory_name)

    try:
        os.mkdir(path)

    except OSError:

        print("File already exists. Please try again")


def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """
    file_to_remove = object_name

    path = os.path.join(current_working_directory, file_to_remove)

    try:
        if os.path.isfile(path):
            os.remove(path)

        elif os.path.isdir(path):
            shutil.rmtree(path)

        else:
            print("File/Directory path can not be removed")

    except FileNotFoundError as e:
        print("File/Directory path can not be removed")


def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """

    file_content = receive_message_ending_with_token(service_socket, 1024, eof_token)

    path = current_working_directory

    file = file_name

    with open(os.path.join(path, file), 'wb') as f:
        f.write(file_content)


def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """

    path = os.path.join(current_working_directory, file_name)
    print("File path in handle dl")
    print(path)

    try:
        if os.path.exists(path):
            file = file_name
            with open(path, 'rb') as f:
                fdata = f.read()
                file_with_eof = fdata + bytes(eof_token, encoding='utf-8')

            service_socket.sendall(file_with_eof)
            msg = service_socket.recv(1024).decode()


        else:
            service_socket.sendall(b""+eof_token.encode())
            msg = service_socket.recv(1024).decode()

    except FileNotFoundError as e:
        service_socket.sendall(str.encode("File does not exits" + eof_token))
        msg = service_socket.recv(1024).decode()
        print("No such file or directory")


class ClientThread(Thread):
    def __init__(self, service_socket : socket.socket, address : str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address

    def run(self):
        print("Connection from : ", self.address)

        random_eof_token = generate_random_eof_token()

        cwd = os.getcwd()

        self.service_socket.sendall(str.encode(random_eof_token))

        ack_msg = self.service_socket.recv(1024).decode()

        print(ack_msg)

        cwd_message = f'The current working directory is "{get_working_directory_info(os.getcwd())}"' \
                      f'{random_eof_token}'

        self.service_socket.sendall(str.encode(cwd_message))

        while True:

            client_command = receive_message_ending_with_token(self.service_socket, 1024, random_eof_token).decode()
            print()

            if client_command.split()[0] == "cd":
                cwd = handle_cd(cwd, client_command.split()[1])

            elif client_command.split()[0] == "mkdir":
                handle_mkdir(cwd, client_command.split()[1])

            elif client_command.split()[0] == "rm":
                handle_rm(cwd, client_command.split()[1])

            elif client_command.split()[0] == "ul":
                handle_ul(cwd, client_command.split()[1], self.service_socket, random_eof_token)

            elif client_command.split()[0] == "dl":
                handle_dl(cwd, client_command.split()[1], self.service_socket, random_eof_token)

            elif client_command.split()[0] == "exit":
                break

            updated_cwd_message = get_working_directory_info(cwd) + random_eof_token

            self.service_socket.sendall(str.encode(updated_cwd_message))

        self.service_socket.close()

        print('Connection closed from:', self.address)


def main():
    HOST = "172.17.0.6"
    PORT = 62214

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            client_thread = ClientThread(conn, addr)
            client_thread.start()



if __name__ == '__main__':
    main()


