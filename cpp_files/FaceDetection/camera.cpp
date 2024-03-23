#include <opencv2/opencv.hpp>

int main() {
    // Load the pre-trained face detection classifier
    cv::CascadeClassifier faceCascade;
    if (!faceCascade.load(cv::samples::findFile("haarcascades/haarcascade_frontalface_default.xml"))) {
        std::cerr << "Error: Unable to load face detection cascade classifier." << std::endl;
        return 1;
    }

    // Open the default camera (usually the webcam)
    cv::VideoCapture cap(0);

    // Check if the camera opened successfully
    if (!cap.isOpened()) {
        std::cerr << "Error: Unable to open the camera." << std::endl;
        return 1;
    }

    // Create a window to display the camera feed
    cv::namedWindow("Face Detection", cv::WINDOW_NORMAL);

    while (true) {
        cv::Mat frame;
        // Capture frame-by-frame
        cap >> frame;

        // Check if the frame is empty
        if (frame.empty()) {
            std::cerr << "Error: Unable to capture frame." << std::endl;
            break;
        }

        // Convert frame to grayscale (required for face detection)
        cv::Mat gray;
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

        // Detect faces
        std::vector<cv::Rect> faces;
        faceCascade.detectMultiScale(gray, faces, 1.1, 4, 0, cv::Size(30, 30));

        // Draw rectangles around detected faces
        for (const auto& face : faces) {
            cv::rectangle(frame, face, cv::Scalar(0, 255, 0), 2);
        }

        // Display the frame with detected faces
        cv::imshow("Webcam", frame);

        // Check for ESC key press
        if (cv::waitKey(1) == 27)
            break;
    }

    // Release the camera and close the window
    cap.release();
    cv::destroyAllWindows();

    return 0;
}
