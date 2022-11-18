import time

import drowsy_yawn_detection
from drowsy_yawn_detection import *
import lane_detection
import object_detection
import pedestrian_detection


def test_face_landmark_detectors():
	assert drowsy_yawn_detection.haar_cascade_face_detector == "dependencies/haarcascade_frontalface_default.xml"
	assert drowsy_yawn_detection.dlib_facial_landmark_predictor == "dependencies/shape_predictor_68_face_landmarks.dat"


def test_drowsy_alert():
	drowsy_yawn_detection.EYE_THRESH_COUNTER = 50
	assert generate_alert(0.24, 11) is drowsy_yawn_detection.drowsy_alert
	assert generate_alert(0.25, 10) is None
	assert generate_alert(0.25, 5) is None
	assert generate_alert(0.30, 0) is None
	time.sleep(2)


def test_yawn_alert():
	drowsy_yawn_detection.YAWN_THRESH_COUNTER = 50
	assert generate_alert(0.25, 11) is drowsy_yawn_detection.yawn_alert
	assert generate_alert(0.25, 10) is None
	assert generate_alert(0.25, 5) is None
	assert generate_alert(0.30, 0) is None


def test_eye_aspect_ratio():
	eye_shape_1 = [[282, 90], [290, 86], [297, 87], [303, 91], [297, 93], [289, 92]]
	eye_shape_2 = [[250, 85], [65, 20], [33, 99], [400, 51], [32, 77], [89, 20]]
	
	assert eye_aspect_ratio(eye_shape_1) == 0.2873592025525141
	assert eye_aspect_ratio(eye_shape_2) == 0.14961377773601023


def test_mouth_aspect_ratio():
	mouth_shape = [
		[210, 91], [209, 107], [209, 122], [211, 138],
		[214, 154], [221, 168], [230, 181], [242, 191],
		[257, 195], [273, 194], [288, 186], [302, 177],
		[314, 165], [321, 150], [324, 134], [328, 118],
		[330, 102], [219, 75], [225, 66], [236, 65],
		[247, 67], [258, 71], [274, 72], [285, 69],
		[297, 68], [309, 71], [316, 82], [265, 82],
		[264, 92], [263, 101], [262, 111], [249, 123],
		[255, 125], [261, 128], [269, 126], [275, 125],
		[230, 87], [235, 84], [243, 84], [250, 88],
		[242, 89], [235, 89], [282, 90], [290, 86],
		[297, 87], [303, 91], [297, 93], [289, 92],
		[235, 147], [245, 143], [254, 141], [260, 143],
		[267, 142], [276, 145], [287, 150], [275, 158],
		[265, 161], [258, 162], [251, 161], [243, 156],
		[239, 148], [253, 148], [259, 149], [267, 148],
		[282, 151], [266, 151], [258, 152], [252, 151]]
	
	assert lip_distance(mouth_shape) == 11.166666666666686
