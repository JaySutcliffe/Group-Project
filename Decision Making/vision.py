#!/usr/bin/env python
# coding: utf-8

# Using https://www.pyimagesearch.com/2016/02/15/determining-object-color-with-opencv/ to work coordinates for tokens based on colour.
# 
# https://jakevdp.github.io/blog/2017/12/05/installing-python-packages-from-jupyter/ for downloading packages in Notebook.

# In[275]:


# Install a pip package in the current Jupyter kernel
# import sys
# !{sys.executable} -m pip install --upgrade imutils
# !{sys.executable} -m pip install --upgrade opencv-python
# !{sys.executable} -m pip install --upgrade keyboard


# In[276]:


# import the necessary packages
import argparse
import imutils
import cv2
import numpy as np


# In[277]:


# CONSTANTS

# Constant for where the camera is
# 0 is where the black player sits
# 1 is side of board turning 90 degrees anticlockwise
# 2 is where the white player sits
# 3 is 90 degrees clockwise from where the black player sits
BOARD_SIDE = 2
BOARD_ANGLE = BOARD_SIDE * 90

SPIKE_WIDTH = 1 / 13
SPIKE_RADIUS = SPIKE_WIDTH / 2
SPIKE_HEIGHT = 8.5 / 22
MIDDLE_HEIGHT = 1 - (2 * SPIKE_HEIGHT)

# BLACK_COLOUR_LOWER = [50,87,105]
BLACK_COLOUR_LOWER = [46,78,95]
BLACK_COLOUR_HIGHER = [179,255,255]

WHITE_COLOUR_LOWER = [50,0,200]
WHITE_COLOUR_HIGHER = [179,255,255]

BORDER_COLOUR_LOWER = [25,105,149]
BORDER_COLOUR_HIGHER = [60,255,255]

TOKEN_RADIUS = SPIKE_RADIUS
TOKEN_GAP = SPIKE_WIDTH + 0.2 / 22

debug = False

# https://www.pyimagesearch.com/2014/08/04/opencv-python-color-detection/ using to mask the image to only deal with parts of a certain colour.


def debug_log(image, name = "Computer Vision"):
    # Function to log images taken
    # If debug is turned on windows will be opened
    # displaying the camera image when playing
    if debug:
        cv2.imshow(name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    cv2.imwrite("./logs/" + name + ".jpg", image)


def get_shapes(image, lower, upper, seperate = False, name = ""):
    lower = np.array(lower, dtype = "uint8")
    upper = np.array(upper, dtype = "uint8")
    
    # Our image is already white on black, but we apply grayscale
    # again, blur the image for better detection and then apply
    # a threshold.
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    image = cv2.bitwise_and(image, image, mask = mask)
    
    debug_log(image, "Mask " + name)
    
    cnt = None
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_OTSU)[1]
    
    if seperate:
        # This is code found from the internet to seperate blobs into circles
        kernel = np.ones((3,3),np.uint8)
        # Removes small unwanted features
        opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
        # sure background area
        # sure_bg = cv2.dilate(opening,kernel,iterations=3)
        # Finding sure foreground area
        # Further away a point is from an edge the grayer it becomes
        dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
        # Binarise with threshold and end up with the white parts
        ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        # unknown = cv2.subtract(sure_bg,sure_fg)
        
        debug_log(sure_fg, "Split " + name)
        
        # We find the contours on the small circles calculated from the code
        cnts = cv2.findContours(sure_fg.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    else:
        # If we do not want to seperate the circles we simply find contours
        # on a copy of the threshold
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        
    # find the colors within the specified boundaries and apply the mask
    
    # Each element has the form (x,y,area)
    xs = [];
    ys = [];
    areas = []; 
    
    # Contours are a curve that joins all the continous points
    # around an object with a specific colour intensity.
    # in openCV this is finding white objects on a black background.
    cnts = imutils.grab_contours(cnts)
    
    
    # loop over the contours
    for c in cnts:
        # Compute the center of the contour
        M = cv2.moments(c) # Weighted average of pixel intensities
    
        # Computing the coordinates of the centre of each token.
        # Coordinates are relative to the image.
        # So they are on a 1200 by 720 grid.
    
        # Small amount of the colour picked up, ignore as no area so
        # will not be a token.
        if M["m00"] <= 0: continue
        
        xs.append(M["m10"] / M["m00"])
        ys.append(M["m01"] / M["m00"])
        
        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])
        
        # Code off of the internet that can plot the contours.
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv2.circle(image, (x, y), 7, (255, 255, 255), -1)       
        cv2.putText(image, "center", (x - 20, y - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
    debug_log(image, "Centers " + name)
    
    return np.vstack((xs,ys))




def perspective_transform(image):
    
    pts = np.transpose(get_shapes(image, BORDER_COLOUR_LOWER, BORDER_COLOUR_HIGHER, False, "Border"))
    rect = np.zeros((4, 2), dtype = "float32")

    a = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(a)]
    rect[3] = pts[np.argmax(a)]

    b = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(b)]
    rect[2] = pts[np.argmax(b)]

    (tl, tr, bl, br) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([[0, 0],[maxWidth , 0],[0, maxHeight],[maxWidth, maxHeight]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    pt = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, pt, (maxWidth, maxHeight))
    
    return warped
    
    

def report_positions(image):
    # Getting the dimensions so the image coordinates
    # can be mapped to a 1 x 1 grid
    height, width, channels = image.shape

    # Getting all of the black tokens
    black = get_shapes(image, BLACK_COLOUR_LOWER, BLACK_COLOUR_HIGHER, True, "Black")
    black[0] = black[0] / width
    black[1] = black[1] / height
    
    # Getting all of the white tokens
    white = get_shapes(image, WHITE_COLOUR_LOWER, WHITE_COLOUR_HIGHER, True, "White")
    white[0] = white[0] / width
    white[1] = white[1] / height
    
    # Creating a matrix each column contains details of each token
    black = np.vstack((black, np.array([1] * black.shape[1])))
    white = np.vstack((white, np.array([0] * white.shape[1])))
    tokens = np.hstack((black, white))
    
    # Creating bins dividing the the grid into spikes, 
    x_inds = np.digitize(tokens[0], SPIKE_WIDTH * np.arange(1,13))
    y_inds = np.digitize(tokens[1], [SPIKE_HEIGHT, SPIKE_HEIGHT + MIDDLE_HEIGHT])
    
    
    bar_black = []
    bar_white = []
    board = [[]] * 24

    for i in range(0,tokens.shape[1]):
        s = tokens[:,i]
        x = x_inds[i]
        y = y_inds[i]
        
        # Middle section of the board
        if y == 1 or x == 6:
            # If white
            if abs(s[2] < 0.05):
                bar_white = bar_white + [(s[0],s[1])]
            else:
                bar_black = bar_black + [(s[0],s[1])]
        else:
            # Subtracting 1 as the divider is also a bin
            if x > 6:
                x -= 1
            if y == 0:
                board[23-x] = board[23-x] + [s]
            else:
                board[x] = board[x] + [s]
                
    return (board, bar_black, bar_white)


def count_colours(spike):
    # Dealing with floating points so do not want to do ==
    spike = spike
    # Counting the number of tokens labelled black and the number labelled white
    colours = np.array([spike[i][2] for i in range(0,len(spike))])
    black_count = sum(np.where(colours > 0.95, 1, 0))
    white_count = sum(np.where(colours < 0.01, 1, 0))
    # Returning a pair to indicate the colour and count
    if black_count == 0:
        if white_count == 0:
            return ("N", 0)
        else:
            return ("W", white_count)
    else:
        if white_count == 0:
            return ("B", black_count)
        else:
            return ("E", black_count - white_count)



def abstract_board(board):
    return [count_colours(spike) for spike in board]


class VisionError(Exception):
    # Base class for exceptions for computer vision
    pass

class CameraReadError(VisionError):
    # Exception raised for error reading from the camera.
    def __init__(self, message):
        self.message = message

class BoardStateError(VisionError):
    # Exepction raised for multiple colours appear to be on the same spike
    def __init__(self, message):
        self.message = message
        
class MoveRegisteredError(VisionError):
    # Exception raised for multiple pieces being knocked off from one spike
    def __init__(self, message):
        self.message = message


# TEST BOARDS

test_board1 = [("W", 2),("N", 0),("N", 0),("N", 0),("N", 0),("B", 5),
                 ("N", 0),("B", 3),("N", 0),("N", 0),("N", 0),("W", 5),
                 ("B", 5),("N", 0),("N", 0),("N", 0),("W", 3),("N", 0),
                 ("W", 5),("N", 0),("N", 0),("N", 0),("N", 0),("B", 2)]

test_board2 = [("W", 1),("W", 1),("N", 0),("N", 0),("N", 0),("B", 5),
              ("N", 0),("B", 3),("N", 0),("N", 0),("N", 0),("W", 5),
              ("B", 5),("N", 0),("N", 0),("N", 0),("W", 3),("N", 0),
              ("W", 5),("N", 0),("N", 0),("N", 0),("N", 0),("B", 2)]


test_board3 = [("W", 1),("W", 1),("N", 0),("N", 0),("N", 0),("B", 5),
              ("B", 2),("B", 1),("N", 0),("N", 0),("N", 0),("W", 5),
              ("B", 5),("N", 0),("N", 0),("N", 0),("W", 3),("N", 0),
              ("W", 5),("N", 0),("N", 0),("N", 0),("N", 0),("B", 2)]


test_board4 = [("W", 1),("W", 1),("N", 0),("N", 0),("N", 0),("B", 5),
              ("B", 2),("B", 1),("N", 0),("N", 0),("N", 0),("W", 5),
              ("B", 5),("N", 0),("N", 0),("N", 0),("W", 3),("N", 0),
              ("W", 2),("W", 1),("B", 2),("W", 2),("N", 0),("N", 0)]



def compare_boards(old_board, new_board):
    # Function to that compares an old board and a new board,
    # I seperated this from the Vision class so I can test it
    # seperately from the camera.
    
    
    # Lists to store if the pieces have been added
    # or removed from a spike.
    add = []
    sub = []
    
    for i in range(0,24):
        # If there is multiple pieces of the same spike.
        if new_board[i][0] == "E":
            raise MoveRegisteredError("Different types on the same spike (" + str(i) + ")")
        
        # If statements to update the add and sub arrays.
        if new_board[i][0] != old_board[i][0]:
            if old_board[i][1] == 1 or new_board[i][0] == "N":
                sub = sub + [(old_board[i][0], old_board[i][1], i)] 
            elif old_board[i][1] > 1:
                # Does some additional move checking to make sure a spike has not completely chaged.
                raise MoveRegisteredError("Multiple pieces knocked off from the same spike " + str(i))
            if new_board[i][1] > 0:
                add = add + [(new_board[i][0], new_board[i][1], i)]
        elif new_board[i][0] != "N":
            diff = new_board[i][1] - old_board[i][1]
            if diff > 0:
                add = add + [(new_board[i][0], diff, i)]
            elif diff < 0:
                sub = sub + [(new_board[i][0], -diff, i)]
    
    return add, sub



# Small test module used when not testing with actual images.
def test_compare():
    add, sub = compare_boards(test_board1,test_board2)
    assert(add == [("W", 1, 1)])
    assert(sub == [("W", 1, 0)])
    add, sub = compare_boards(test_board2,test_board3)
    assert(add == [("B", 2, 6)])
    assert(sub == [("B", 2, 7)])
    add, sub = compare_boards(test_board3,test_board4)
    assert(sorted(add) == sorted([("W", 1, 19), ("W", 2, 21), ("B", 2, 20)]))
    assert(sorted(sub) == sorted([("W", 3, 18), ("B", 2, 23)]))


# In[287]:


class Vision:
    def __init__(self):
        # An abstract representation of the board
        # it may not know the total number of tokens
        # on stacked spikes
        self.abstract = [("W", 2),("N", 0),("N", 0),("N", 0),("N", 0),("B", 5),
                         ("N", 0),("B", 3),("N", 0),("N", 0),("N", 0),("W", 5),
                         ("B", 5),("N", 0),("N", 0),("N", 0),("W", 3),("N", 0),
                         ("W", 5),("N", 0),("N", 0),("N", 0),("N", 0),("B", 2)]
        # Stores the physical positions as well as colours of the pieces
        self.physical = None
        # Stores the physical positions of the knocked out pieces
        self.bar_white = None
        self.bar_black = None
        # The index of the webcam
        self.camera_index = 1
        
        self.free_spot = (SPIKE_WIDTH * 6.5, TOKEN_RADIUS)
        
        
        
    def get_move(self, dm_move):
        player, start, end = dm_move
        
        self.update_board()
        
        # Position moving from and moving to
        pos0 = None
        pos1 = None
        
        if start == "BAR":
            # Just choose the maximum piece to move off of
            # the knocked out section.
            if player == 0:
                pos0 = max(self.bar_white)
            else:
                pos0 = max(self.bar_black)
        else:
            # The computer is always white, modify to respect
            # the black board.
            start = 23 - start
            
            # Getting outmost piece on the spike
            token = None
            if start < 12:
                token = np.amin(self.physical[start], axis = 0)
            else:
                token = np.amax(self.physical[start], axis = 0)
            pos0 = (token[0], token[1])
                
        if end == "BAR":
            # If we move a piece to knocked out we can just choose
            # a suitable position for the arm to put the piece down at
            pos1 = self.free_spot
            if len(self.bar_black) == 0:
                self.free_spot = (self.free_spot[0], TOKEN_RADIUS)
            else:
                self.free_spot = (self.free_spot[0], self.free_spot[1] + TOKEN_GAP)
        elif end == "OFF":
            # Moving it off the board
            pos1 = "OFF"
        else:
            # Modifying output to respect black player board
            end = 23 - end
            
            # Translating the position into an x value from 0 to 12
            x = end
            if x > 11:
                x = 23 - x
            if x > 5:
                x += 1
            
            if end < 12:
                # Nothing on the spike so generate a position
                if len(self.physical[end]) == 0:
                    # Finding a suitable position on the empty spike
                    # If it is near the coloured edge markers 
                    # move it slightly further up
                    if x == 0 or x == 12:
                        pos1 = (SPIKE_WIDTH * x + SPIKE_RADIUS, 1 - 2 * TOKEN_RADIUS)
                    else:
                        pos1 = (SPIKE_WIDTH * x + SPIKE_RADIUS, 1 - TOKEN_RADIUS)
                else:
                    # Find next available space on the spike
                    pos1 = (SPIKE_WIDTH * x + SPIKE_RADIUS,
                            (np.amin(self.physical[end], axis = 0))[1] - TOKEN_GAP)
            else:
                if len(self.physical[end]) == 0:
                    if x == 0 or x == 12:
                        pos1 = (SPIKE_WIDTH * x + SPIKE_RADIUS, 2 * TOKEN_RADIUS)
                    else:
                        pos1 = (SPIKE_WIDTH * x + SPIKE_RADIUS, TOKEN_RADIUS)
                else:
                    pos1 = (SPIKE_WIDTH * x + SPIKE_RADIUS,
                           (np.amax(self.physical[end], axis = 0))[1] + TOKEN_GAP)
                    
        return (pos0, pos1)
        
        
    def update_board(self):
        # Capturing the image from a camera
        cam = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        retrieved, image = cam.read()
        
        if retrieved == False:
            raise CameraReadError("Error reading from webcam")
        
                
        # Rotating the image
        height, width, channels = image.shape
        M = cv2.getRotationMatrix2D((width / 2, height / 2), BOARD_ANGLE, 1)
        image = cv2.warpAffine(image, M, (width, height))
        
        debug_log(image, "Image taken")
        
        # Transforming the image to only include the board
        image = perspective_transform(image)
        
        debug_log(image, "Image transformed")
        
        # Retrieving the piece details from the board
        self.physical, self.bar_black, self.bar_white = report_positions(image)
        old_board = self.abstract
        
        self.abstract = abstract_board(self.physical)
        
        cam.release()
        cv2.destroyAllWindows() # Handles the releasing of the camera accordingly
        
        # Returning old board so it can be used for comparisons
        return old_board
        
        
    def test_play(self):
        while input("Capture image before move...  (q and enter to quit)") != "q":
            try:
                self.update_board()
                input("Capture image after move... ")
                old_board = self.update_board()
                add, sub = compare_boards(old_board, self.abstract)
                print(self.abstract)
                print(len(self.bar_white))
                print(len(self.bar_black))
                print(add)
                print(sub)
            except VisionError as e:
                print("Error with move: " + e.message)
                
    def take_turn(self):
        # Function that takes two images and compares them, reporting changes
        # in the board for computer vision to use
        while True:
            try:
                input("Capture image before move... ")
                self.update_board()
                input("Capture image after move... ")
                
                old_board = self.update_board()
                add, sub = compare_boards(old_board, self.abstract)
                return (len(self.bar_black), len(self.bar_white), add, sub)
            except VisionError as e:
                print("Error with move: " + e.message)

    
def test_get_move():
    v = Vision()
    v.update_board()
    print("WHITE OUT -> 12")
    print(v.get_move((1, "BAR", 11)))
    print("BLACK 4 -> 9")
    print(v.get_move((0, 4, 9)))
    print("BLACK 0 -> 23")
    print(v.get_move((0, 0, 23)))
    
    
# test_get_move()


def test_image():
    # Testing to see if pieces and the border is detected
    
    #cam = cv2.VideoCapture(0)
    #retrieved, image = cam.read()
    retrieved = True
    if retrieved:
        # Showing the image before the transformation
        image = cv2.imread('WhiteBlue3.jpg')
        cv2.imshow('board.jpg',image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Transforming and showing the new image
        image = perspective_transform(image)
        cv2.imshow('board.jpg',image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        board, k1, k2 = report_positions(image)
        
        # Printing out the knocked of pieces and the abstract board
        print(k1)
        print(k2)
        print(abstract_board(board))
    else:
        print("Error reading from webcam")
        cv2.destroyAllWindows()
        

