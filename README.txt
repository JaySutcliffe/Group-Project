Before running:
The webcam must be connected via USB to a device with a monitor and a keyboard. 
The EV3 must also be connected following the guide: 
https://www.ev3dev.org/docs/tutorials/connecting-to-the-internet-via-usb/. 
The webcam must be positioned such that all 4 yellow corners are visible in 
the centre of the image displayed. This can be verified using the camera app, 
or by checking the log files produced when running. Pytorch, openCV (cv2), numpy and imutils 
must all be installed on the device.

File to run:
The file to be run is ‘game.py’. The program is then blocked until ‘c.py’ 
is selected to run on the EV3.

How to play:
The player is always assigned to play as the colour black and the computer white. 
The computers move will be carried out by the robot arm. In the case that an error message arises 
when the arm is moving, the camera fails to detect the piece to move. 
On clicking enter, the process is tried again. When the player takes their turn, 
they must click enter to submit two images. The first is an image of the board state before the move. 
If pieces are being moved onto a spike with 5 tokens, tokens must be stacked such that the before and 
after image clearly shows the difference and number of tokens added or removed from the spike. 
The player has to make all of the changes to the board before taking another image. 
In the event of a camera problem or a problem detecting a move, the board must be reset, 
and images retaken.

Spotting problems:
Inside the log folder, every image taken related to the current camera. 
To verify the camera is correctly working see if all pieces are picked up in the ‘Center Black’ 
and ‘Center White’ images. The board state before taking a turn can be seen in the play log file. 
The arrays list the number of tokens on each spike the orders with respect to each colour’s home.
