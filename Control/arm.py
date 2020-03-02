import math
import time

import s
import translation as t

# Speeds of the motors
LARGE_MAX_SPEED = 100
MEDIUM_MAX_SPEED = 200
SPEED_THETA = 0.45 * LARGE_MAX_SPEED
SPEED_SHOULDER = 1.00 * LARGE_MAX_SPEED
SPEED_ELBOW = 0.25 * LARGE_MAX_SPEED
SPEED_CLAW = 0.25 * MEDIUM_MAX_SPEED

# Gear ratios of the motors
GEAR_THETA = 21
GEAR_SHOULDER = 66.68
GEAR_ELBOW = 5

# Motor addresses for the server->ev3 communications
MOTOR_THETA = 'A'
MOTOR_SHOULDER = 'B'
MOTOR_ELBOW = 'C'
MOTOR_CLAW = 'D'

# Constant amount to wait at the end of each move
WAIT_CONST = 1

# Claw positions (not covered in inverse kinematics because extremely simple)
CLAW_EXTENDED_POS = 200
CLAW_WAIT_CONST = 0

# Height of the top of pieces above the base
PIECE_HEIGHT = 10

# Position off the board for between moves and dropping won pieces
OFF_POSITION = (-200, -100, 100)
# Neutral position
REST_POS = (110, 110, 100 + PIECE_HEIGHT)


class Arm:
    '''
        Initializing the arm initializes the connection with the EV3 and moves the arm to a neutral position
    '''

    def __init__(self, host=s.HOST, port=s.PORT):
        # Initialize server-client communications with EV3, using the default host and port if not specified
        self.server = s.Server(host, port)
        # Assumes shoulder starts at backstop, elbow starts aligned with shoulder, pointing directly forward
        self.angle_pos = (180, 83, 83)
        # Assumes claw starts retracted
        self.claw_retracted = True
        # Immediately move to rest position, which initializes cart_pos
        self.move_to(*REST_POS)

    '''
    Moves a piece from (x1,y1) to (x2,y2), or from (x1,y1) to 'OFF', which means to drop the piece off the board
    '''

    def move_piece(self, instructions):
        (from_x, from_y), to_coord = instructions
        # Collect piece
        self.collect_or_drop(from_x, from_y, pick_up=True)
        # Either discard or place
        if to_coord == 'OFF':
            self.drop_piece()
        else:
            to_x, to_y = to_coord
            self.collect_or_drop(to_x, to_y, pick_up=False)

    '''
        Move to off_board location and drop any held piece
    '''

    def drop_piece(self):
        self.move_to(*OFF_POSITION, steps=2)
        self.retract_claw()

    '''
        Alias for easy use
    '''

    def move_out_of_way(self):
        self.drop_piece()

    '''
        Carefully move to above the piece, then slowly lower and pick up or deposit piece, then return to neutral
    '''

    def collect_or_drop(self, x, y, pick_up):
        if self.cart_pos != REST_POS:
            self.move_to(*REST_POS, steps=2)
        self.move_to(x, y, 50 + PIECE_HEIGHT, steps=2)
        self.move_to(x, y, PIECE_HEIGHT, steps=3)
        self.move_claw(pick_up)
        self.move_to(x, y, 50 + PIECE_HEIGHT, steps=3)
        self.move_to(*REST_POS, steps=2)

    '''
        Move the claw, picking a piece up if pick_up is True
        and dropping the piece if pick_up is False
    '''

    def move_claw(self, pick_up):
        if pick_up:
            self.extend_claw()
        else:
            self.retract_claw()

    '''
        Moves to the position x,y,z, doing the move in the number of steps specified
        Blocks until the move is completed
    '''

    def move_to(self, x, y, z, steps=1):
        # Use the same move_to function for each of the steps
        if steps > 1:
            # Calculate how much to move in each step ans where to start from
            x_step = (x - self.cart_pos[0]) / steps
            y_step = (y - self.cart_pos[1]) / steps
            z_step = (z - self.cart_pos[2]) / steps
            start_x, start_y, start_z = self.cart_pos

            for i in range(1, steps + 1):
                # Move incrementally, linearly interpolating between the start and end positions
                self.move_to(start_x + x_step * i, start_y + y_step * i, start_z + z_step * i, steps=1)
        # Single movement
        else:
            # Update store of position
            self.cart_pos = (x, y, z)

            # Calculate positions
            theta, shoulder, elbow = t.transform(x, y, z)
            theta = math.degrees(theta)
            shoulder = math.degrees(shoulder)
            elbow = math.degrees(elbow)

            # Transformation assumes theta=0 points forward, but EV3 assumes 180 is pointing forward,
            # so adjust by 180 to correct
            self.server.send_pos(MOTOR_THETA, int((theta + 180) * GEAR_THETA))
            self.server.send_pos(MOTOR_SHOULDER, int(shoulder * GEAR_SHOULDER))
            self.server.send_pos(MOTOR_ELBOW, int(elbow * GEAR_ELBOW))

            # Calculate amount of time to wait for EV3 to finish (send_pos is non-blocking)
            theta_time = abs(self.angle_pos[0] - theta - 180) / SPEED_THETA
            shoulder_time = abs(self.angle_pos[1] - shoulder) / SPEED_SHOULDER
            elbow_time = abs(self.angle_pos[2] - elbow) / SPEED_ELBOW
            time.sleep(theta_time + shoulder_time + elbow_time + WAIT_CONST)

            # Update store of arm position
            self.angle_pos = (theta + 180, shoulder, elbow)

    # Only move claw if it isn't already in the correct position
    def retract_claw(self):
        if not self.claw_retracted:
            self.server.send_pos(MOTOR_CLAW, 0)
            # Waits for the same amount of time as to extend the claw
            time.sleep(CLAW_EXTENDED_POS / SPEED_CLAW + CLAW_WAIT_CONST)
            self.claw_retracted = True

    def extend_claw(self):
        if self.claw_retracted:
            self.server.send_pos(MOTOR_CLAW, CLAW_EXTENDED_POS)
            time.sleep(CLAW_EXTENDED_POS / SPEED_CLAW + CLAW_WAIT_CONST)
            self.claw_retracted = False

    # Magic positions that set the claw to the start state for easy reset
    def reset(self):
        self.server.send_pos(MOTOR_THETA, (180) * 21)
        self.server.send_pos(MOTOR_SHOULDER, int(66.68 * 83))
        self.server.send_pos(MOTOR_ELBOW, 5 * 83)
        self.server.send_pos(MOTOR_CLAW, 0)
