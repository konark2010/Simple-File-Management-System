<h1 align="center">
  <br>
  
Simple-File-Management-System

  <br>
</h1>


**Project Description:**

The Simple File Management System is a network-based file management application comprising both a client (`client.py`) and a server (`server.py`). This project provides users with the ability to remotely manage files and directories on a central server through a command-line interface. It allows users to navigate directories, create new directories, remove files and directories, upload files to the server, and download files from the server.

**Client (`client.py`):**
- The client application initiates a socket connection to the server, enabling communication over the network.
- A handshake is performed with the server to establish a secure communication channel, involving the exchange of an end-of-file (EOF) token to mark the end of messages.
- The client displays the current working directory received from the server upon connection.
- Users can input various commands, such as changing directories (`cd`), creating directories (`mkdir`), removing files or directories (`rm`), uploading files to the server (`ul`), and downloading files from the server (`dl`).
- The client continuously accepts user commands and sends them to the server for execution.
- Users can exit the application gracefully by issuing the "exit" command.

**Server (`server.py`):**
- The server application listens for incoming connections on a specified host and port.
- It generates a random EOF token used to signify the end of messages exchanged between the client and server, enhancing message integrity.
- For each incoming client connection, a new thread (`ClientThread`) is created to handle the client's requests concurrently, allowing multiple clients to interact with the server simultaneously.
- The server responds to client commands, executes file management operations, sends file content when requested, and provides information about the current working directory.
- It handles various client commands, including changing directories (`cd`), creating directories (`mkdir`), removing files or directories (`rm`), uploading files from clients (`ul`), and downloading files to clients (`dl`).
- The server maintains the integrity of file operations, ensuring that directories and files are managed correctly.

**Usage:**
1. Start the server (`server.py`) on a host and port of your choice.
2. Run multiple instances of the client (`client.py`) on different machines or terminals to connect to the server.
3. Clients can interact with the server by entering commands via the command-line interface.
4. The server responds to client commands, executes requested actions, and provides feedback to clients.
5. Clients can gracefully exit the application by issuing the "exit" command.
