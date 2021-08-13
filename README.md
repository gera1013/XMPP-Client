# XMPP-Client
Client implementing the existing XMPP protocol

## Installation
* Open terminal and run command (using pip) <pre> pip install -r requirements.txt</pre>
* After the libraries are installed, to start the client run <pre> python main.py </pre> 

## Functionalities
The implementation is capable of the following
* Account registration
* Logging in and out of the server
* Sending and receiveng files
* Multi-user chat room
* 1-to-1 message communication
* Client's roster visualization
* Adding contacts to the client's roster
* Presence and status changes
* Chat status notifications
* Removing an existing account

## File description
* `main.py` file with the main program, creates Client object and does basic I/O operations
* `client.py` file with the client module, contains the class Client and implements the mentioned functionalities
* `util.py` file with utilities. Text formatting, functions and imports
* `requirements.txt` file with all the needed python libraries
