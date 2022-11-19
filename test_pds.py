import os
import time
import pedestrian_detection
from pedestrian_detection import *


def test_hogcv():
	assert "cv2.HOGDescriptor" in str(HOGCV)