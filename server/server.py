import websockets
import asyncio
from cvzone.FaceDetectionModule import FaceDetector

import cv2, base64

port = 80

print("Started server on port : ", port)

async def transmit(websocket, path):
    print("Client Connected !")
    await websocket.send("Connection Established")
    try :
        
        #Raspberry Pi Camera
        #cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        cap = cv2.VideoCapture(0) 
        detector = FaceDetector(minDetectionCon=0.5)

        while cap.isOpened():
            _, frame = cap.read()
            frame = cv2.flip(frame,1)

            frame, bboxs = detector.findFaces(frame)
            
            encoded = cv2.imencode('.jpg', frame)[1]

            data = str(base64.b64encode(encoded))
            data = data[2:len(data)-1]
            
            await websocket.send(data)
            
            # cv2.imshow("Transimission", frame)
            
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        cap.release()
    except websockets.connection.ConnectionClosed as e:
        print("Client Disconnected !")
        cap.release()
    # except:
    #     print("Someting went Wrong !")

start_server = websockets.serve(transmit, host="192.168.0.170", port=port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()