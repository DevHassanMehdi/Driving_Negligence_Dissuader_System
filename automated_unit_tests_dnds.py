import time
from __init__ import *
import lane_detection
from lane_detection import *
from object_detection import *
from pedestrian_detection import *
import drowsy_yawn_detection
from drowsy_yawn_detection import *

# Test __init__.py
widgets_list = [
	"header",
	"footer",
	"start_dds",
	"start_lds",
	"start_ods",
	"start_pds",
	"start_dnds",
	"close_reset_dnds",
	"theme_change",
	"show_mar_dds",
	"show_ear_dds",
	"stop_button_dds",
	"stop_button_lds",
	"stop_button_ods",
	"stop_button_pds",
	"stop_button_dnds",
	"video_feed_dds",
	"video_feed_lds",
	"video_feed_ods",
	"video_feed_pds",
	"show_curve_radius_lds",
	"show_curve_offset_lds",
	"status_update_dds",
	"status_update_lds",
	"show_detection_stats_ods",
	"show_detection_stats_pds"]


# Test existence all widgets
def test_widgets_dictionary():
	for widget in widgets_list:
		assert widget in widgets


# Test existence of light stylesheet
def test_light_stylesheet_exists():
	assert "/* This is the end of light stylesheet */" in light_style


# Test existence of dark stylesheet
def test_dark_stylesheet_exists():
	assert "/* This is the end of dark stylesheet */" in dark_style


# Test drowsy_yawn_detection.py
dds_test_image = cv.imread("dependencies/testing_images/dds_test_image.jpeg")
gray_image = cv.cvtColor(dds_test_image, cv.COLOR_BGR2GRAY)
faces = detect_faces(gray_image)[0]
for x, y, w, h in faces:
	face_landmarks = detect_facial_landmarks(x, y, w, h, gray_image)[0]
	eye = final_eye_aspect_ratio(face_landmarks)
	final_ear = eye[0]
	left_eye = eye[1]
	right_eye = eye[2]


# Test existence of Haar cascade classifier and DLib shape predictor
def test_face_landmark_detectors():
	assert "cv2.CascadeClassifier" in str(face_detector)
	assert "shape_predictor" in str(landmark_predictor)


# Test DDS alert system for drowsiness
def test_drowsy_alert():
	drowsy_yawn_detection.EYE_THRESH_COUNTER = 50
	time.sleep(2)
	assert generate_alert(0.24, 11) is drowsy_yawn_detection.drowsy_alert
	assert generate_alert(0.25, 10) is None
	assert generate_alert(0.25, 5) is None
	assert generate_alert(0.30, 0) is None


# Test DDS alert system for Yawning
def test_yawn_alert():
	drowsy_yawn_detection.YAWN_THRESH_COUNTER = 50
	time.sleep(2)
	assert generate_alert(0.25, 11) is drowsy_yawn_detection.yawn_alert
	assert generate_alert(0.25, 10) is None
	assert generate_alert(0.25, 5) is None
	assert generate_alert(0.30, 0) is None


# Test face doctor function
def test_faces():
	assert detect_faces(gray_image)[-1] is True


# Test landmark detector function
def test_facial_landmarks():
	assert detect_facial_landmarks(x, y, w, h, gray_image)[-1] is True


# Test EAR function
def test_eye_aspect_ratio():
	# Left eye starting and ending point
	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
	# right eye starting and ending point
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
	
	left_eye_shape = face_landmarks[lStart:lEnd]
	right_eye_shape = face_landmarks[rStart:rEnd]
	
	assert eye_aspect_ratio(left_eye_shape) == 0.3664208133564902
	assert eye_aspect_ratio(right_eye_shape) == 0.3467036334036159


# Test MAR function
def test_mouth_aspect_ratio():
	assert lip_distance(face_landmarks) == 81.83333333333337


# Test draw detection functions
def test_draw_eyes_lips():
	assert draw_eyes_lips(left_eye, right_eye, face_landmarks, dds_test_image) is True


# Test lane_detection.py
lds_test_image = cv.imread("dependencies/testing_images/lds_test_image.png")
test_object = Lane(orig_frame=lds_test_image)


# Test alert system for lane left side
def test_lane_alert_left():
	lane_detection.LANE_THRESH_COUNTER = 50
	assert lane_detection.generate_alert(151) is lane_detection.lane_alert
	time.sleep(2)
	assert lane_detection.generate_alert(150) is None
	assert lane_detection.generate_alert(100) is None
	assert lane_detection.generate_alert(50) is None
	assert lane_detection.generate_alert(0) is None


# Test alert system for lane right side
def test_lane_alert_right():
	lane_detection.LANE_THRESH_COUNTER = 50
	assert lane_detection.generate_alert(-151) is lane_detection.lane_alert
	time.sleep(2)
	assert lane_detection.generate_alert(-150) is None
	assert lane_detection.generate_alert(-100) is None
	assert lane_detection.generate_alert(-50) is None
	assert lane_detection.generate_alert(0) is None


# Test lane line marking function
def test_lane_lines():
	assert test_object.get_line_markings()[-1] is True


# Test Perspective transform function
def test_perspective_transform():
	assert test_object.perspective_transform()[-1] is True


# Test histogram functions
def test_histogram():
	assert test_object.calculate_histogram(plot=False)[-1] is True
	assert test_object.histogram_peak() == (1005, 2118)


# Test lane overlay function
def test_lanes_overlay():
	left_fit, right_fit = test_object.get_lane_line_indices_sliding_windows()
	test_object.get_lane_line_previous_window(left_fit, right_fit, plot=False)
	assert test_object.overlay_lane_lines(plot=False)[-1] is True


# Test road curvature function
def test_curvature():
	assert test_object.calculate_curvature(print_to_terminal=False) == (59.27039207604876, 80.9157531072003)
	assert test_object.calculate_curve_radius() == "Curve Radius: 70.1"


# Test Center offset function
def test_center_offset():
	assert test_object.calculate_car_position(print_to_terminal=False) == -233.16285434727652
	assert test_object.calculate_curve_offset() == "Curve Offset: -233.2"


# object_detection
ods_test_image = cv.imread("dependencies/testing_images/ods_test_image.png")
results = detect_objects(ods_test_image)


# Test existence of yolo model
def test_yolo_model():
	assert os.path.basename(model_dir) == "yolov5n.pt"


# Test object detection function
def test_detect_objects():
	assert "1 person, 5 cars, 3 trucks, 1 traffic light" in str(results)


# Test statistics extraction function
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


# Test frame squeezing function
def test_squeeze_frame():
	frame = np.squeeze(results.render())
	assert str(frame.shape) == "(1620, 2880, 3)"


# Test pedestrian_detection.py
image = cv.imread("dependencies/testing_images/pds_test_image.png")
rects, weights, pick, person = detect_persons(image)


# Test existence of HOGDescriptor
def test_hogcv():
	assert "cv2.HOGDescriptor" in str(HOGCV)


# Test person detection function
def test_detect_persons():
	assert str(rects) == "[[2203  347 2331  603]]"
	assert str(weights) == "[    0.19352]"
	assert str(pick) == "[[2203  347 2331  603]]"
	assert str(person) == "1"


# Test drawing results function
def test_draw_bounding_boxes():
	assert draw_bounding_boxes(pick, image) is None
