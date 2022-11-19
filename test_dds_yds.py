import time
import drowsy_yawn_detection
from drowsy_yawn_detection import *

image = cv.imread("dependencies/images/dds_test_image.jpeg")
gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def test_face_landmark_detectors():
	assert "cv2.CascadeClassifier" in str(face_detector)
	assert "shape_predictor" in str(landmark_predictor)


def test_drowsy_alert():
	drowsy_yawn_detection.EYE_THRESH_COUNTER = 50
	time.sleep(2)
	assert generate_alert(0.24, 11) is drowsy_yawn_detection.drowsy_alert
	assert generate_alert(0.25, 10) is None
	assert generate_alert(0.25, 5) is None
	assert generate_alert(0.30, 0) is None


def test_yawn_alert():
	drowsy_yawn_detection.YAWN_THRESH_COUNTER = 50
	time.sleep(2)
	assert generate_alert(0.25, 11) is drowsy_yawn_detection.yawn_alert
	assert generate_alert(0.25, 10) is None
	assert generate_alert(0.25, 5) is None
	assert generate_alert(0.30, 0) is None


def test_faces():
	assert detect_faces(gray_image)[-1] is True


faces = detect_faces(gray_image)[0]

for x, y, w, h in faces:
	face_landmarks = detect_facial_landmarks(x, y, w, h, gray_image)[0]
	eye = final_eye_aspect_ratio(face_landmarks)
	final_ear = eye[0]
	left_eye = eye[1]
	right_eye = eye[2]


def test_facial_landmarks():
	assert detect_facial_landmarks(x, y, w, h, gray_image)[-1] is True


def test_eye_aspect_ratio():
	# Left eye starting and ending point
	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
	# right eye starting and ending point
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
	
	left_eye_shape = face_landmarks[lStart:lEnd]
	right_eye_shape = face_landmarks[rStart:rEnd]
	
	assert eye_aspect_ratio(left_eye_shape) == 0.3664208133564902
	assert eye_aspect_ratio(right_eye_shape) == 0.3467036334036159


def test_mouth_aspect_ratio():
	assert lip_distance(face_landmarks) == 81.83333333333337


def test_draw_eyes_lips():
	assert draw_eyes_lips(left_eye, right_eye, face_landmarks, image) is True
