import math
import time
from s import *

board_width = 220
board_depth = 220
arm_to_board = 200  

STUD_LENGTH = 7.985

angled_beam_angle = math.acos(3 / 5)
elbow_down_length = 4 * STUD_LENGTH
elbow_across_length = 23 * STUD_LENGTH
elbow_length = math.sqrt(elbow_across_length ** 2 + elbow_down_length ** 2
                         - 2 * elbow_across_length * elbow_down_length * math.cos(angled_beam_angle + math.pi / 2))
# elbow_angle_from_horiz = math.acos((-elbow_down_length**2+elbow_across_length**2+elbow_length**2)/(2*elbow_across_length*elbow_length))
shoulder_length = 25 * STUD_LENGTH

horizontal_arm_offset = 0 * STUD_LENGTH
base_height_offset = 7 * STUD_LENGTH
claw_height_offset = 2 * STUD_LENGTH + STUD_LENGTH/2
claw_length_offset = 10 * STUD_LENGTH


# Original coordinate system uses corner of board close right to arm as (0,0,0)
# Define y to be direction from arm to board
# x is to right
# theta=0 points directly at the center of the board
# theta progresses counterclockwise

# Use base of arm as center of the world
def board_to_arm_centric(x, y, z):
    return board_width / 2 - x, y + arm_to_board, z


def arm_centric_to_arm_cylindrical(x, y, z):
    theta = math.atan2(y, x)
    r = math.sqrt(x ** 2 + y ** 2)
    # Slight difference due to offset of arm from center
    arm_r = math.sqrt(r ** 2 - horizontal_arm_offset ** 2)
    arm_angle = theta - math.atan2(horizontal_arm_offset, arm_r)

    return arm_angle - math.pi / 2, arm_r, z


def offset_arm_plane(r, z):
    z = z - base_height_offset
    z = z + claw_height_offset
    r = r - claw_length_offset
    return r, z


def arm_coordinates_to_angle(r, z):
    r_sphere = math.sqrt(r ** 2 + z ** 2)
    phi = math.atan2( z,  r ) 
    return r_sphere, phi


# Motor angles measured from 0 is in front of the arm
def arm_angle_to_motor_angles(r, phi):
    # alpha = a_shoulder-phi
    alpha = math.acos((shoulder_length ** 2 + r ** 2 - elbow_length ** 2) /
                      (2 * shoulder_length * r))
    a_shoulder = alpha + phi

    beta = math.acos((shoulder_length ** 2 + elbow_length ** 2 - r ** 2) /
                     (2 * shoulder_length * elbow_length))

    a_elbow = beta + a_shoulder - math.pi / 2

    # adjust for the angled piece on the elbow
    a_elbow = a_elbow + angled_beam_angle
    return a_shoulder, a_elbow


def transform(x, y, z):
    theta, r, z = arm_centric_to_arm_cylindrical(*board_to_arm_centric(x, y, z))
    #cubic = (295.3898) + (-3.30652 * r) + (0.011514 * r**2) + (-1.39483e-5 * r**3)
    cubic = (295.3898) + (-3.30652 * r) + (0.011514 * r**2) + (-1.39483e-5 * r**3)
    z_corrected = z
    print(cubic)
    print(z_corrected)
    shoulder, elbow = arm_angle_to_motor_angles(*arm_coordinates_to_angle(*offset_arm_plane(r, z)))
    #shoulder_offset = (-0.05161 * r) + (0.00122 * z) + 4.35543
    #elbow_offset = (-0.02777 * r) + (-0.07052 * z) + 24.82531
    #shoulder_offset = math.radians(shoulder_offset)
    #elbow_offset = math.radians(elbow_offset)
    print("Transform : (" + str(theta) + ", " + str(shoulder) + ", " + str(elbow) + ")")
    print("r: " + str(r))
    #return theta, shoulder - shoulder_offset, elbow + elbow_offset
    return theta, shoulder, elbow


def relative_transform(x, y, z):
    theta, r, z = arm_centric_to_arm_cylindrical(x, y, z)
    shoulder, elbow = arm_angle_to_motor_angles(*arm_coordinates_to_angle(*offset_arm_plane(r, z)))
    print("Relative Transform: (" + str(theta) + ", " + str(shoulder) + ", " + str(elbow) + ")")
    return theta, shoulder, elbow

def coord_to_motor(x, y, z):
    theta, shoulder, elbow = transform(x, y, z)
    print(str(math.degrees(theta)) + " " + str(math.degrees(shoulder)) + " " + str(math.degrees(elbow)))
    return int(7 * (math.degrees(theta) + 90)), int(66.68 * math.degrees(shoulder)), int(5 * math.degrees(elbow))

    

def main():
    s = Server(HOST, PORT)
    #theta, shoulder, elbow = coord_to_motor(0, 0 , 50)
    #s.send_pos('A', theta)
    #s.send_pos('C', elbow)
    #s.send_pos('B', shoulder)
    #s.send_pos('D', 250)
    
    
    while (angles := input()) != 'q':
        l = angles.split(",")
        x = int(l[0])
        y = int(l[1])
        z = int(l[2])
        theta, shoulder, elbow = transform(x,y,z)
        s.send_pos('A', int(7 * (math.degrees(theta) + 90)))
        s.send_pos('B', int(66.68 * math.degrees(shoulder)))
        s.send_pos('C', int(5 * math.degrees(elbow)))
        
    
    
    s.send_pos('A', 90*7)
    s.send_pos('B', int(66.68*90))
    s.send_pos('C', 5*90)
    s.send_pos('D', 0)
        

if __name__== "__main__":
    main()
