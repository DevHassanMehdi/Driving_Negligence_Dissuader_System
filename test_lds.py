import time
import lane_detection
from lane_detection import *

image = cv.imread("dependencies/images/lds_test_image.png")
test_object = Lane(orig_frame=image)


def test_lane_alert_left():
	lane_detection.LANE_THRESH_COUNTER = 50
	assert generate_alert(151) is lane_detection.lane_alert
	time.sleep(2)
	assert generate_alert(150) is None
	assert generate_alert(100) is None
	assert generate_alert(50) is None
	assert generate_alert(0) is None


def test_lane_alert_right():
	lane_detection.LANE_THRESH_COUNTER = 50
	assert generate_alert(-151) is lane_detection.lane_alert
	time.sleep(2)
	assert generate_alert(-150) is None
	assert generate_alert(-100) is None
	assert generate_alert(-50) is None
	assert generate_alert(0) is None


def test_lane_lines():
	assert test_object.get_line_markings()[-1] is True


def test_perspective_transform():
	assert test_object.perspective_transform()[-1] is True


def test_histogram():
	assert test_object.calculate_histogram(plot=False)[-1] is True
	assert test_object.histogram_peak() == (679, 2330)


def test_lanes_overlay():
	left_fit, right_fit = test_object.get_lane_line_indices_sliding_windows()
	test_object.get_lane_line_previous_window(left_fit, right_fit, plot=False)
	assert test_object.overlay_lane_lines(plot=False)[-1] is True


def test_curvature():
	assert test_object.calculate_curvature(print_to_terminal=False) == (101.41419227314752, 73.81808794080365)
	assert test_object.calculate_curve_radius() == "Curve Radius: 87.6"


def test_center_offset():
	assert test_object.calculate_car_position(print_to_terminal=False) == -373.3344238145847
	assert test_object.calculate_curve_offset() == "Curve Offset: -373.3"
