import cv2
from cvzone.FaceDetectionModule import FaceDetector

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize Face Detector
detector = FaceDetector()

while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img)

    # Display the output
    cv2.imshow("Output", img)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()
