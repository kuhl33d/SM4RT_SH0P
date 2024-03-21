import os

# Ensure live_feed directory exists
live_feed_dir = os.path.join(os.getcwd(), 'live_feed')
if not os.path.exists(live_feed_dir):
    os.makedirs(live_feed_dir)

def process_image(img, file_path):
    corners, ids, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(img, corners, ids)
        rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)
        for rvec, tvec in zip(rvecs, tvecs):
            cv2.drawFrameAxes(img, camera_matrix, dist_coeffs, rvec, tvec, 0.03)
    # Save processed image to disk
    cv2.imwrite(file_path, img)

@socketio.on('image')
def handle_image(data):
    client_id = request.cookies.get('ClientID')
    if client_id:
        print("Receiving data from:", client_id)
        img_data = data['data']
        img_data = base64.b64decode(img_data.split(",")[1])
        nparr = np.frombuffer(img_data, np.uint8)
        try:
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            file_path = os.path.join(live_feed_dir, f"{client_id}.jpg")
            process_image(img, file_path)
        except Exception as e:
            print(f"Error while processing {client_id}: {e}")
