import asyncio
import cv2
import re
import servoModule  # Assuming this module exists and provides servo control
from FaceDetector import FaceDetector  # Assuming this module exists and provides face detection
import websockets  # Assuming this module is imported

async def vision(websocket):
    try:
        servoX_pin = 15
        servoY_pin = 14

        servoXi = 1500
        servoYi = 1500

        pwm = servoModule.PCA9685(0x40, debug=False)
        pwm.setPWMFreq(50)
        pwm.setServoPulse(servoX_pin, servoXi)
        pwm.setServoPulse(servoY_pin, servoYi)

        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CV_CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, 240)

        detector = FaceDetector(minDetectionCon=0.5)

        while cap.isOpened():
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)

            FD_frame, FD_bboxs = detector.findFaces(frame)

            myList = []

            # Compute area of BBOXs
            for bbox in FD_bboxs:
                x, y, w, h = bbox["bbox"]
                area = w * h
                bbox["area"] = area
                myList.append(bbox)

            # if myList is empty
            if not myList:
                pass
            else:
                # Compares between dicts in list, select dict with higher AREA
                max_area_dict = max(myList, key=lambda x: x["area"])
                if max_area_dict:
                    center = max_area_dict["center"]
                    coordinates = str(center)
                    x_coords, y_coords = re.findall(r'\d+', coordinates)
                    x_coords = int(x_coords)
                    y_coords = int(y_coords)

                    # Quadratic to simulate acceleration:

                    # Check whether to move left or right:
                    # center-x = 160, center-y = 120
                    if x_coords < 160:
                        servoXi += 10
                    elif x_coords > 160:
                        servoXi -= 10

                    if y_coords < 120:
                        servoYi += 10
                    elif y_coords > 160:
                        servoYi -= 10

                    pwm.setServoPulse(servoX_pin, servoXi)
                    pwm.setServoPulse(servoY_pin, servoYi)

            # Send frame to client if connected
            if websocket:
                encoded = cv2.imencode('.jpg', frame)[1].tobytes()
                data = bytes(encoded)
                await websocket.send(data)

    except Exception as e:
        print("Something went wrong:", e)
        cap.release()

async def main(websocket, path):
    await vision(websocket)

start_server = websockets.serve(main, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
