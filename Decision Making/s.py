import socket
import time

#run on pi

HOST = '10.42.0.1'  #USB interface to EV3
#HOST = '192.168.137.1'
#HOST = 'localhost'
PORT = 65432

class Server:   
    
    #Sets up server socket and accepts connection
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen()
        self.conn, self.addr = self.s.accept()
        print('Connected to', self.addr)
    
    #closes socket at end of session
    def __del__(self):
        print("Socket closed")
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()   
    
    '''
    Motor commands consist of 
        motor: a string specifying the port the motor is connected to A - D
        position: an int, where each position increment is a one degree change in angle
    '''
    def send_pos(self, motor, position):
        msg = motor + str(max(position, 0)) + ";"
        self.conn.sendall(bytes(msg, 'utf-8'))
        print(msg)
    
    def receive(self):
        return self.conn.recv(1024)
  
def main():
    s = Server(HOST, PORT)
    for i in range(5):
        s.send_pos('A', i*360)
        #time.sleep(5)
    s.send_pos('A', 0)

if __name__== "__main__":
    main()
