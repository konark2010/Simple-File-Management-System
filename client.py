import socket
import os


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
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


def initialize(host, port):
    """
    1) Creates a socket object and connects to the server.
    2) receives the random token (10 bytes) used to indicate end of messages.
    3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param host: the ip address of the server
    :param port: the port number of the server
    :return: the created socket object
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print('Connected to server at IP:', host, 'and Port:', port)

    eof_token = s.recv(1024).decode()

    print('Handshake Done. EOF is:', eof_token)

    eof_token_acknowledgement = f"I received the eof_token and I acknowledge that"

    s.sendall(eof_token_acknowledgement.encode())

    cwd = receive_message_ending_with_token(s, 1024, eof_token).decode()

    print(cwd)

    return [s, eof_token]


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_input = command_and_arg

    client_input_with_token = client_input + eof_token

    client_socket.sendall(client_input_with_token.encode())

    new_cwd = receive_message_ending_with_token(client_socket, 1024, eof_token).decode()

    print(new_cwd)


def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_input = command_and_arg

    client_input_with_token = client_input + eof_token

    client_socket.sendall(client_input_with_token.encode())

    new_cwd = receive_message_ending_with_token(client_socket, 1024, eof_token).decode()

    print(new_cwd)


def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_input = command_and_arg

    client_input_with_token = client_input + eof_token

    client_socket.sendall(client_input_with_token.encode())

    new_cwd = receive_message_ending_with_token(client_socket, 1024, eof_token).decode()

    print(new_cwd)


def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_input = command_and_arg

    client_input_with_token = client_input + eof_token

    client_socket.sendall(client_input_with_token.encode())

    file_name = command_and_arg.split()[1]

    try:
        os.path.isfile(file_name)
        with open(file_name, 'rb') as f:

            file_content = f.read()

            file_content_with_token = file_content + bytes(eof_token, encoding='utf-8')

            client_socket.sendall(file_content_with_token)

            new_cwd = receive_message_ending_with_token(client_socket, 1024, eof_token).decode()

            print(new_cwd)

    except FileNotFoundError as e:
        print("No such file or directory")


def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """
    client_input = command_and_arg

    client_input_with_token = client_input + eof_token

    client_socket.sendall(str.encode(client_input_with_token))

    file_name = command_and_arg.split()[1]

    file_content = receive_message_ending_with_token(client_socket, 1024, eof_token)

    if len(file_content) != 0:
        with open(file_name, 'wb') as f:
            f.write(file_content)

        client_socket.sendall(str.encode("File downloaded successfully"))

        new_cwd = receive_message_ending_with_token(client_socket, 1024, eof_token).decode()

    else:
        client_socket.sendall(str.encode("Received blank file" + eof_token))

        new_cwd = receive_message_ending_with_token(client_socket, 1024, eof_token).decode()
        print(" No such file or directory")


def main():
    HOST = "172.17.0.6"  # The server's hostname or IP address
    PORT = 62214  # The port used by the server

    s, eof_token = initialize(HOST, PORT)

    while True:

        client_input = input("Enter the command you want to perform on the current Directory:")
        if client_input != "":
            if client_input.split()[0].lower() == "cd":
                issue_cd(client_input, s, eof_token)

            elif client_input.split()[0].lower() == "mkdir":
                issue_mkdir(client_input, s, eof_token)

            elif client_input.split()[0].lower() == "rm":
                issue_rm(client_input, s, eof_token)

            elif client_input.split()[0].lower() == "ul":
                issue_ul(client_input, s, eof_token)

            elif client_input.split()[0].lower() == "dl":
                issue_dl(client_input, s, eof_token)

            elif client_input.split()[0].lower() == "exit":
                print('Exiting the application.')
                s.sendall(str.encode(client_input.split()[0].lower() + eof_token))
                break

            else:
                print("Please enter any valid command")
        else:
            print("Please enter any command")


if __name__ == '__main__':
    main()