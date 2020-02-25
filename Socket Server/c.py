#!/usr/bin/env python3
#from ev3dev.ev3 import *
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, LargeMotor, MediumMotor
import socket

#runs on ev3

HOST = '10.42.0.1'
#HOST = 'localhost'
PORT = 65432
MOTORS =     ['A','B','C','D']
MOTORSPEED = [ 25, 25, 25, 25]

class Client:
    
    def __init__(self, host, port):
        self.partial = ""
        self.values = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))        
    
    def __del__(self):
        self.s.close()        
    
    def send_sensor(self, sensor, value):
        msg = sensor + str(value) + ";"
        self.conn.sendall(bytes(msg, 'utf-8'))
        print(i)        
    
    def receive(self):
        data = self.s.recv(1024)
        self.process(data)
        
    def get_values(self):
        self.receive()
        return self.values
        
    def process(self, data):
        element = ""
        for c in self.partial + data.decode("utf-8"):
            if not c == ";":
                element += c
            else:
                self.values.append(element)
                element = ""
        self.partial = element
    
    def pop_value(self, n = 1):
        self.values = self.values[n:]
        

class RobotArm:
    
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
            
    def move(self, motor, angle):
        if motor == 'A':
            self.motorA.on_to_position(SpeedPercent(MOTORSPEED[0]), angle)
        elif motor == 'B':
            self.motorB.on_to_position(SpeedPercent(MOTORSPEED[1]), angle)
        elif motor == 'C':
            self.motorC.on_to_position(SpeedPercent(MOTORSPEED[2]), angle)
        elif motor == 'D':
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
