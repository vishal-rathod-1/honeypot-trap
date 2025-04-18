# Libraries
import logging 
from logging.handlers import RotatingFileHandler
import socket
import threading
import paramiko
# Constants
logging_format = logging.Formatter('%(message)s')


SSH_BANNER = "SSH-2.0-MySSHServer_1.0"
host_key=paramiko.RSAKey(filename='server.key')
#host_key = 'server.key'
# Logger and Logging files


funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audit.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('cmd_audit.log', maxBytes=2000, backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)


# Emulated Shell

def emulated_shell(channel, client_ip):
    channel.send(b"corporate-jumpbox2$ ")
    command = b""
    while True:  
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()

        command += char
        # Emulate common shell commands.
        if char == b"\r":
            if command.strip() == b'exit':
                response = b"\n Goodbye!\n"
                channel.close()
            elif command.strip() == b'pwd':
                response = b"\n" + b"\\usr\\local" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()}' + "executed by " f'{client_ip}')
            elif command.strip() == b'whoami':
                response = b"\n" + b"corpuser1" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()}' + "executed by " f'{client_ip}')
            elif command.strip() == b'ls':
                response = b"\n" + b"jumpbox1.conf" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()}' + "executed by " f'{client_ip}')
            elif command.strip() == b'cat jumpbox1.conf':
                response = b"\n" + b"Go to deeboodah.com" + b"\r\n"
                funnel_logger.info(f'Command {command.strip()}' + "executed by " f'{client_ip}')
            else:
                response = b"\n" + bytes(command.strip()) + b"\r\n"
                funnel_logger.info(f'Command {command.strip()}' + "executed by " f'{client_ip}')
            creds_logger.info(f'command {command.strip()} executed by {client_ip}')
            channel.send(response)
            channel.send(b"corporate-jumpbox2$ ")
            command = b""
            
# SSH server + socket's
# SSH Server Class. This establishes the options for the SSH server.
class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        
    def get_allowed_auth(self):
        return "password"
    
    def check_auth_password(self , username, password):
        funnel_logger.info(f"client{self.client_ip} attempted connection with username: {username} password : {password}")
        creds_logger.info(f"{self.client_ip}, {username} , {password}")
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
             return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL

        
    def check_channel_shell_request(self, channel):
          self.event.set()
          return True
    
    def check_channel_pty_request(self , channel,term , width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel,command):
        command = str(command)
        return True
    
def client_handle(client, addr , username, password):
    client_ip = addr[0]
    print(f"{client_ip} has connected to the server")
    
    try: 
        transport = paramiko.Transport(client)
        transport.local_version=SSH_BANNER
        server = Server(client_ip=client_ip , input_username=username, input_password=password)
        
        transport.add_server_key(host_key)

        transport.start_server(server=server)
        
        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened")
        
        standard_banner = "Welcome to Ubunutu 22.04 LTS (Vishal)!\r\n\r\n"
        channel.send(standard_banner)
        emulated_shell(channel,client_ip=client_ip)
        
    except Exception as error:
        print(error)
        print("!!! Error !!!")
                
    finally:
        try:
            transport.close()
        except Exception as error:
            print(error)
            print("!! Error !!!")
        client.close()
        
# Provision SSH - based Honeypot

def honeypot(address, port, username, password):
                                #ipv4           #tcp stream
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address,int(port)))
    
    socks.listen(100) # limit till 100 connection
    print(f"SSH server is listening on port {port}.")
    
    while True:
        try:
            client , addr =socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client,addr,username,password))
            ssh_honeypot_thread.start()
            
        except Exception as error:
            print(error)
            
honeypot('127.0.0.1','2233','username', 'password')