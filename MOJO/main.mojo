from python import Python

def main():
    Python.add_to_path("/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/")
    let numpy = Python.import_module("numpy")
    print("Loaded numpy")
    let cv2 = Python.import_module("cv2")
    print("Loaded cv2")

    face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    video_capture = cv2.VideoCapture(0)
    # # /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/cv2/__init__.py

    while True:
        capture_attempt = video_capture.read()
        result = capture_attempt[0]
        video_frame = capture_attempt[1]

        gray_image = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray_image, 1.1, 5)
        
        for value in faces:
            x = value[0]
            y = value[1]
            w = value[2]
            h = value[3]
            arg1 = [x, y]
            print(arg1)
            # cv2.rectangle(video_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    #     cv2.imshow('Video', video_frame)
