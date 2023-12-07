from python import Python, PythonObject

def main():
    Python.add_to_path("/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/")
    let numpy = Python.import_module("numpy")
    print("Loaded numpy")
    let cv2 = Python.import_module("cv2")
    print("Loaded cv2")

    # LOADING CASCASE
    face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # CAPTURING WEBCAM
    cap = cv2.VideoCapture(0)

    while True:
        capture = cap.read()
        success = capture[0]
        img = capture[1]
        img = cv2.flip(img,1)

        # GRAY-SCALING
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_classifier.detectMultiScale(gray, 1.1, 5)

        for value in faces:
            # PythonObjects
            x = value[0]
            y = value[1]
            w = value[2]
            h = value[3]

            # change all PythonObj to Int
            int_x = x.to_float64().to_int()
            int_y = y.to_float64().to_int()
            int_w = w.to_float64().to_int()
            int_h = h.to_float64().to_int()
            
            let arg2: Tuple[Int, Int] = (int_x, int_y)

            let xplusw = int_x + int_w
            let yplush = int_y + int_h

            let arg3: Tuple[Int, Int] = (xplusw, yplush)

            let arg4: Tuple[Int, Int, Int] = (0, 255, 0)

            img = cv2.rectangle(img, arg2, arg3, arg4, 2)

        cv2.imshow("EYE(i) ROBOT", img)
        cv2.waitKey(1)