import os
import time
import object_detection
from object_detection import *

image = cv.imread("dependencies/images/ods_test_image.png")
results = detect_objects(image)


def test_yolo_model():
	assert os.path.basename(model_dir) == "yolov5n.pt"


def test_detect_objects():
	assert "1 person, 5 cars, 3 trucks, 1 traffic light" in str(results)


def test_extract_detection_data():
	data = results.pandas().xyxy[0].sort_values('class')
	data.to_numpy()
	stats = f'' \
		f'Person: {np.count_nonzero(data == "person")}   ' \
		f'Cycle: {np.count_nonzero(data == "bicycle")}   ' \
		f'Bike: {np.count_nonzero(data == "motorcycle")}   ' \
		f'Car: {np.count_nonzero(data == "car")}   ' \
		f'Bus: {np.count_nonzero(data == "bus")}   ' \
		f'Truck: {np.count_nonzero(data == "truck")}'
	assert stats == "Person: 1   Cycle: 0   Bike: 0   Car: 5   Bus: 0   Truck: 3"
	
	
def test_squeeze_frame():
	frame = np.squeeze(results.render())
	assert str(frame.shape) == "(1620, 2880, 3)"
