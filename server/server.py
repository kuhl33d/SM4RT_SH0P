from flask import Flask, request, redirect, url_for
from flask_socketio import SocketIO
import cv2
import numpy as np
import base64
import os
import hashlib
from uuid import uuid4
import shutil
from threading import Lock

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)

# Placeholder for camera calibration data and ArUco detection parameters
camera_matrix = np.array([[800, 0, 640], [0, 800, 360], [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1), dtype=np.float32)
parameters = cv2.aruco.DetectorParameters_create()
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)

# Directory for storing live feed images
live_feed_dir = os.path.join(os.getcwd(), 'live_feed')

# Clean the live_feed directory on each new run
if os.path.exists(live_feed_dir):
    shutil.rmtree(live_feed_dir)
os.makedirs(live_feed_dir)

# Store the last checksum for each client
last_checksums = {}

# Lock for thread-safe writing to the updated_clients file
file_lock = Lock()

# Clear the updated_clients.txt file on server start
with open('updated_clients.txt', 'w') as file:
    file.truncate(0)

@app.route('/')
def index():
    response = app.make_response(redirect(url_for('static', filename='camera.html')))
    client_id = uuid4().hex
    response.set_cookie('ClientID', client_id)
    return response

def write_updated_client(client_id):
    """Append the client's UUID to updated_clients.txt."""
    with file_lock:
        with open('updated_clients.txt', 'a') as file:
            file.write(client_id + '\n')

def process_image(img, file_path, client_id):
    """Process and save the image if it's new, and update the client tracking file."""
    corners, ids, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(img, corners, ids)
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)
        for rvec, tvec in zip(rvecs, tvecs):
            cv2.drawFrameAxes(img, camera_matrix, dist_coeffs, rvec, tvec, 0.03)
    checksum = hashlib.sha256(cv2.imencode('.jpg', img)[1]).hexdigest()
    if client_id not in last_checksums or last_checksums[client_id] != checksum:
        cv2.imwrite(file_path, img)
        last_checksums[client_id] = checksum
        write_updated_client(client_id)
        print(f"new image: {client_id}")

@socketio.on('connect')
def handle_connect():
    client_id = request.cookies.get('ClientID')
    print(f"Client {client_id} connected.")

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.cookies.get('ClientID')
    file_path = os.path.join(live_feed_dir, f"{client_id}.jpg")
    if os.path.exists(file_path):
        os.remove(file_path)
    if client_id in last_checksums:
        del last_checksums[client_id]

@socketio.on('image')
def handle_image(data):
    client_id = request.cookies.get('ClientID')
    if client_id:
        img_data = data['data']
        img_data = base64.b64decode(img_data.split(",")[1])
        nparr = np.frombuffer(img_data, np.uint8)
        try:
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            file_path = os.path.join(live_feed_dir, f"{client_id}.jpg")
            process_image(img, file_path, client_id)
        except Exception as e:
            print(f"Error while processing from {client_id}: {e}")

@socketio.on('heartbeat')
def handle_heartbeat(data):
    # Heartbeat received, can be used for keeping the connection alive
    print(f"Heartbeat received from {request.cookies.get('ClientID')}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False, ssl_context=('cert.pem', 'key.pem'))
