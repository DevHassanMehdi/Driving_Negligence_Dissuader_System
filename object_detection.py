# PREP DEPENDENCIES
from PyQt5.QtCore import Qt, pyqtSignal, QThread  # To send out video frames to our PyQt5 GUI page
from PyQt5.QtGui import QImage  # To convert the OpenCV frames into PyQt5 image
import numpy as np  # For Sci-Calculations
import cv2 as cv  # For enabling computer vision
import torch  # For Sci-Computation

# Load the yolo-v5 nano model
model = torch.hub.load('dependencies/yolov5', 'custom', path='dependencies/yolov5/models/yolov5n.pt', source="local")

global odsDetectionStats


# Object Detection Thread class (The ODS will run in a separate thread when called by the start button from GUI pge)
class StartODS(QThread):
    # Variable that will be sent to GUI page
    ImageUpdate = pyqtSignal(QImage)
    odsDetectionStats = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.ThreadActive = None
    
    # Object Detection begins here (The method will run when the thread starts)
    def run(self):
        # Activating thread
        global odsDetectionStats
        self.ThreadActive = True
        # Capture video
        video_stream = cv.VideoCapture("dependencies/video/dash.mp4")
        # While the ODS thread is active, Do detections
        while self.ThreadActive:
            # Split video into frames
            ret, frame = video_stream.read()
            if ret:
                try:
                    # Resizing Frames
                    frame = cv.resize(frame, (640, 360))
                
                    # Detect objects
                    frame = model(frame)
                    data = frame.pandas().xyxy[0].sort_values('class')
                    data = data.to_numpy()
                    
                    # Extract the number of each listed object detected and send it to GUI page
                    odsDetectionStats = f'' \
                                        f'Person: {np.count_nonzero(data == "person")}   ' \
                                        f'Cycle: {np.count_nonzero(data == "bicycle")}   ' \
                                        f'Bike: {np.count_nonzero(data == "motorcycle")}   ' \
                                        f'Car: {np.count_nonzero(data == "car")}   ' \
                                        f'Bus: {np.count_nonzero(data == "bus")}   ' \
                                        f'Truck: {np.count_nonzero(data == "truck")}'
                    
                    # Convert the processed frame into a numpy array
                    frame = np.squeeze(frame.render())

                except TypeError or ValueError or AttributeError:
                    pass
                # Convert the frame from OpenCV format to PyQt5 format
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                convert_to_qt_format = QImage(
                    frame.data, frame.shape[1],
                    frame.shape[0],
                    QImage.Format_RGB888)
                frame = convert_to_qt_format.scaled(640, 360, Qt.KeepAspectRatio)
            
                # Send the frames and Stats to the GUI window
                self.ImageUpdate.emit(frame)
                self.odsDetectionStats.emit(odsDetectionStats)

        # Close all opened windows and stop video Capture
        video_stream.release()
        cv.destroyAllWindows()
    
    # Thread stop method (De-Activate the thread and Quit the operation when method is called from GUI window)
    def stop(self):
        self.ThreadActive = False
        self.quit()
