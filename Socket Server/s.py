import socket

#run on pi
HOST = '10.42.0.1'
#HOST = 'localhost'
PORT = 65432

class Server:   
    
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen()
        self.conn, self.addr = self.s.accept()
        print('Connected to', self.addr)
    
    def __del__(self):
        print("Socket closed")
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
    
    def send_pos(self, motor, position):
        msg = motor + str(position) + ";"
        self.conn.sendall(bytes(msg, 'utf-8'))
        print(msg)
    
    def receive(self):
        return self.conn.recv(1024)
  
def main():
    s = Server(HOST, PORT)
    for i in range(100):
        s.send_pos('A', i*360)

if __name__== "__main__":
    main()
