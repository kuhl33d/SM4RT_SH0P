import mediapipe as mp
import cv2
import socket
from threading import Timer, Thread, Event
import base64
import time
interested_in = 8 

class HandPointsSender(Thread):
    def __init__(self, client_socket, event):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.stopped = event
        self.data = ""
        self.sent = False

    def run(self):
        print("HandPointsSender thread started.")
        while not self.stopped.is_set():
            if self.data != "" and self.sent == False:
                self.client_socket.send(base64.b64encode(bytes(self.data, 'utf-8')))
                self.sent = True
                # time.sleep(0.1)


cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)
Hands = mp.solutions.hands.Hands(static_image_mode=False,max_num_hands=1,min_detection_confidence=0.7)
util = mp.solutions.drawing_utils
style = mp.solutions.drawing_styles

stopFlag = Event()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'  
port = 12345  
server_socket.bind((host, port))
server_socket.listen(1)

print("Waiting for a client to connect...")
client_socket, client_address = server_socket.accept()
print(f"Connected to {client_address}")

hand_points_sender_thread = HandPointsSender(client_socket, stopFlag)

hand_points_sender_thread.start()
if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
    while rval:
        rval, frame = vc.read()
        frame = cv2.flip(frame,1)
        key = cv2.waitKey(20)
        if key == 27: # exit on ESC
            break
        #processing
        res = Hands.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        if res.multi_hand_landmarks:
            H = res.multi_hand_landmarks[0] #first hand
            mp.solutions.drawing_utils.draw_landmarks(frame,H,mp.solutions.hands.HAND_CONNECTIONS)
            for id,lm in enumerate(H.landmark):
                height,width,channel = frame.shape
                cx,cy = int(lm.x*width),int(lm.y*height)
                cv2.circle(frame,(cx,cy),5,(255,0,0),cv2.FILLED)
                if (id==interested_in):
                    cv2.circle(frame,(cx,cy),15,(0,255,0),cv2.FILLED)
                    hand_points_sender_thread.data = (f"{cx},{cy},{int(width)},{int(height)}")
                    hand_points_sender_thread.sent = False
                    # hand_points_sender_thread.run()

        cv2.imshow("preview", frame)
else:
    rval = False

stopFlag.set()
hand_points_sender_thread.join()  # Wait for the thread to finish
client_socket.close()
server_socket.close()
vc.release()
cv2.destroyWindow("preview")
