#!/usr/bin/env python3
#from ev3dev.ev3 import *
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, LargeMotor, MediumMotor
import socket

#runs on ev3

HOST = '10.42.0.1'  #USB interface to EV3
#HOST = 'localhost'
PORT = 65432
MOTORS =     ['A','B','C','D']
MOTORSPEED = [ 99, 25, 25, 25] #Sets motor speed as percentage of maximum speed

class Client:
    
    #Connects to socket
    def __init__(self, host, port):
        self.partial = ""
        self.values = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))        
    
    #closes socket at end of session
    def __del__(self):
        self.s.close()        
    
    #NOT CURRENTLY USED
    def send_sensor(self, sensor, value):
        msg = sensor + str(value) + ";"
        self.conn.sendall(bytes(msg, 'utf-8'))
        print(i)        
    
    #Reads data from socket
    def receive(self):
        data = self.s.recv(1024)
        self.process(data)
    
    #Returns queue of decoded messages from server
    def get_values(self):
        self.receive()
        return self.values
    
    #Removes message delimiters
    def process(self, data):
        element = ""
        for c in self.partial + data.decode("utf-8"):
            if not c == ";":
                element += c
            else:
                self.values.append(element)
                element = ""
        self.partial = element
    
    #Removes values from front of message queue
    def pop_value(self, n = 1):
        self.values = self.values[n:]
        

class RobotArm:
    
    #Makes instance of Client, and initialises motors
    #Medium motor MUST be plugged into port D
    def __init__(self):
        self.c = Client(HOST, PORT)
        
        try:
            self.motorA = LargeMotor(OUTPUT_A)
        except:
            print("Large Motor not connected to port A")
        try:
            self.motorB = LargeMotor(OUTPUT_B)
        except:
            print("Large Motor not connected to port B")
        try:
            self.motorC = LargeMotor(OUTPUT_C)
        except:
            print("Large Motor not connected to port C")
        try:
            self.motorD = MediumMotor(OUTPUT_D)
        except:
            print("Medium Motor not connected to port D")
    
    #Takes command from front of message queue and executes it
    def command(self):
        msgs = self.c.get_values()
        if len(msgs) == 0:
            return
        else:
            com = msgs[0]
            self.c.pop_value()
            port = com[0]
            value = int(com[1:])
            if port in MOTORS:
                self.move(port, value)
            else:
                print("Command not recognised: " + com)
    #Moves the motor plugged into port, to the position specified by angle      
    def move(self, port, angle):
        if port == 'A':
            self.motorA.on_to_position(SpeedPercent(MOTORSPEED[0]), angle)
        elif port == 'B':
            self.motorB.on_to_position(SpeedPercent(MOTORSPEED[1]), angle)
        elif port == 'C':
            self.motorC.on_to_position(SpeedPercent(MOTORSPEED[2]), angle)
        elif port == 'D':
            self.motorD.on_to_position(SpeedPercent(MOTORSPEED[3]), angle)
    
        
  
def main():
    r = RobotArm()
    last  = ""
    u_input = ""
    while u_input != 'q':
        #msgs = c.get_values()
        #print(msgs)
        #last = msgs[len(msgs) - 1]
        #c.pop_value(len(msgs))
        r.command()
        
        
    
if __name__== "__main__":
    main()
