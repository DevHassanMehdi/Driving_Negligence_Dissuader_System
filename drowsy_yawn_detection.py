# PREP DEPENDENCIES
from PyQt5.QtCore import Qt, pyqtSignal, QThread  # To send out video frames to our PyQt5 GUI page
from scipy.spatial import distance as dist  # To find point to point distances
from imutils import face_utils  # For image processing on images
from PyQt5.QtGui import QImage  # To convert the OpenCV frames into PyQt5 image
from threading import Thread  # For multi-threading
import numpy as np  # For SCi-Calculations
import cv2 as cv  # For enabling computer vision
import imutils  # For image processing
import dlib  # For face landmark detection
import os  # For System functions

# Haar cascade classifier for face detection
haar_cascade_face_detector = "dependencies/haarcascade_frontalface_default.xml"
face_detector = cv.CascadeClassifier(haar_cascade_face_detector)
# Dlib facial landmark detector
dlib_facial_landmark_predictor = "dependencies/shape_predictor_68_face_landmarks.dat"
landmark_predictor = dlib.shape_predictor(dlib_facial_landmark_predictor)

# Important Variables that will be used throughout the DDS
font = cv.FONT_HERSHEY_DUPLEX

EYE_ASPECT_RATIO_THRESHOLD = 0.25
EYE_CLOSED_THRESHOLD = 10
EYE_THRESH_COUNTER = 0
DROWSY_COUNTER = 0
drowsy_alert = False

MOUTH_ASPECT_RATIO_THRESHOLD = 10
MOUTH_OPEN_THRESHOLD = 10
YAWN_THRESH_COUNTER = 0
YAWN_COUNTER = 0
yawn_alert = False

speech = False


# Alarm system
def generate_alert(final_eye_ratio, upper_lower_lip_distance):
	global EYE_THRESH_COUNTER
	global YAWN_THRESH_COUNTER
	global drowsy_alert
	global yawn_alert
	global speech
	# If eye ratio is below threshold
	if final_eye_ratio < EYE_ASPECT_RATIO_THRESHOLD:
		# Increase counter
		EYE_THRESH_COUNTER += 1
		# If closed eye counter exceeds threshold
		if EYE_THRESH_COUNTER >= EYE_CLOSED_THRESHOLD:
			# Alert the driver
			if not drowsy_alert and not speech:
				drowsy_alert = True
				new_thread = Thread(target=alert)
				new_thread.deamon = True
				new_thread.start()
				return drowsy_alert
	# stop alert on wake-up
	else:
		EYE_THRESH_COUNTER = 0
		drowsy_alert = False
	
	# If mouth ratio is above threshold
	if upper_lower_lip_distance > MOUTH_ASPECT_RATIO_THRESHOLD:
		# Increase counter
		YAWN_THRESH_COUNTER += 1
		# If opened mouth counter exceeds threshold
		if YAWN_THRESH_COUNTER >= MOUTH_OPEN_THRESHOLD:
			# Alert the driver
			if not yawn_alert and not speech:
				yawn_alert = True
				new_thread = Thread(target=alert)
				new_thread.deamon = True
				new_thread.start()
				return yawn_alert
	# stop alert on wake-up
	else:
		YAWN_THRESH_COUNTER = 0
		yawn_alert = False


# Function to alarm the driver when drowsy or yawning
def alert():
	global DROWSY_COUNTER
	global YAWN_COUNTER
	global speech
	# When drowsy
	if drowsy_alert:
		speech = True
		speak = "afplay " + "dependencies/audio/drowsiness-detected.mp3"
		os.system(speak)
		# Increase the drowsy counter
		DROWSY_COUNTER += 1
		speech = False
	# When yawning
	if yawn_alert:
		speech = True
		speak = "afplay " + "dependencies/audio/yawning-detected.mp3"
		os.system(speak)
		# Increase the drowsy counter
		YAWN_COUNTER += 1
		speech = False


# Detect faces
def detect_faces(gray_frame):
	faces = face_detector.detectMultiScale(
		gray_frame, scaleFactor=1.1,
		minNeighbors=5, minSize=(30, 30),
		flags=cv.CASCADE_SCALE_IMAGE)
	return faces, True


# Detected landmarks from faces
def detect_facial_landmarks(x, y, w, h, gray_frame):
	face = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
	# landmarks of the detected face
	face_landmarks = landmark_predictor(gray_frame, face)
	# Convert facial landmark array into numpy array
	face_landmarks = face_utils.shape_to_np(face_landmarks)
	return face_landmarks, True


# Function to calculate eye aspect ratio
def eye_aspect_ratio(eye_marks):
	# upper eyelid points
	upper_eyelid = dist.euclidean(eye_marks[1], eye_marks[5])
	# lower eyelid points
	lower_eyelid = dist.euclidean(eye_marks[2], eye_marks[4])
	# medial and lateral canthus points
	medial_lateral_canthus = dist.euclidean(eye_marks[0], eye_marks[3])
	# ratio = upper_eyelid_points + lower_eyelid_points / 2 x medial_lateral_canthus_points
	aspect_ratio = (upper_eyelid + lower_eyelid) / (2.0 * medial_lateral_canthus)
	
	return aspect_ratio


# Function to define shape of the eye
def final_eye_aspect_ratio(eye_shape):
	# Left eye starting and ending point
	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
	# right eye starting and ending point
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
	
	left_eye_shape = eye_shape[lStart:lEnd]
	right_eye_shape = eye_shape[rStart:rEnd]
	
	left_eye_aspect_ratio = eye_aspect_ratio(left_eye_shape)
	right_eye_aspect_ratio = eye_aspect_ratio(right_eye_shape)
	final_aspect_ratio = (left_eye_aspect_ratio + right_eye_aspect_ratio) / 2.0
	return final_aspect_ratio, left_eye_shape, right_eye_shape


# Function to calculate upper and lower lip distance
def lip_distance(lips_marks):
	# Upper lip points
	upper_lip = lips_marks[50:53]
	upper_lip = np.concatenate((upper_lip, lips_marks[61:64]))
	# Lower lip points
	lower_lip = lips_marks[56:59]
	lower_lip = np.concatenate((lower_lip, lips_marks[65:68]))
	# Mean of upper lip points
	upper_lip_mean = np.mean(upper_lip, axis=0)
	# Mean of lower lip points
	lower_lip_mean = np.mean(lower_lip, axis=0)
	# Absolute distance b/w upper lip and lowe lip
	absolute_lip_distance = abs(upper_lip_mean[1] - lower_lip_mean[1])
	return absolute_lip_distance


# Draw eyes and lips on frames
def draw_eyes_lips(left_eye, right_eye, face_landmarks, frame):
	draw_left_eye = cv.convexHull(left_eye)
	cv.drawContours(frame, [draw_left_eye], -1, (255, 255, 255), 1)
	# Draw detected right eye on each frame
	draw_right_eye = cv.convexHull(right_eye)
	cv.drawContours(frame, [draw_right_eye], -1, (255, 255, 255), 1)
	# Draw detected lips on each frame
	lip = face_landmarks[48:60]
	cv.drawContours(frame, [lip], -1, (255, 255, 255), 1)
	return True


# Drowsiness Detection Thread class (The DDS will run in a separate thread when called by the start button from GUI pge)
class StartDDS(QThread):
	# Variable that will be sent to GUI page
	ImageUpdate = pyqtSignal(QImage)
	DrowsyStats = pyqtSignal(str)
	YawnStats = pyqtSignal(str)
	Status = pyqtSignal(str)
	
	def __init__(self):
		super().__init__()
		self.ThreadActive = None
	
	# Drowsiness Detection begins here (The method will run when the thread starts)
	def run(self):
		drowsy_stats = ""
		yawn_stats = ""
		status = ""
		global drowsy_alert
		global yawn_alert
		
		# Activating thread
		self.ThreadActive = True
		# Start the video stream
		video_stream = cv.VideoCapture("dependencies/video/dds1.mp4")
		# To use camera instead of video file, replace the above code with... video_stream = cv.VideoCapture(0)
		
		# While the DDS thread is active, Do detections
		while self.ThreadActive:
			# Set the FPS cap on video
			cv.waitKey(5)
			# Split video into frames
			ret, frame = video_stream.read()
			if ret:
				try:
					# Resize the frames
					frame = imutils.resize(frame, width=560)
					# convert frames into gray scale
					gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
					
					# Detect faces from the frames
					faces = detect_faces(gray_frame)[0]
					
					# Predict facial landmarks
					for (x, y, w, h) in faces:
						# Detect facial landmarks
						face_landmarks = detect_facial_landmarks(x, y, w, h, gray_frame)[0]
						# Send facial landmarks and get final eye aspect ratio
						eye = final_eye_aspect_ratio(face_landmarks)
						final_ear = eye[0]
						left_eye = eye[1]
						right_eye = eye[2]
						# Send facial landmarks and get upper and lower lip distance
						final_mar = lip_distance(face_landmarks)
						# Draw detected left eye on each frame
						draw_eyes_lips(left_eye, right_eye, face_landmarks, frame)
						# Generate Alert
						generate_alert(final_ear, final_mar)
						# Set the EAR and Drowsy count string that wil be sent to the GUI frame
						drowsy_stats = f"EAR: {round(final_ear, 1)}    Count: {DROWSY_COUNTER}"
						# Set the MAR and Yawn count string that wil be sent to the GUI frame
						yawn_stats = f"MAR: {round(final_mar, 1)}    Count: {YAWN_COUNTER}"
						# Set the alert status that wil be sent to the GUI frame
						if drowsy_alert:
							status = "Drowsiness Detected!"
						elif yawn_alert:
							status = "Yawning Detected!"
						else:
							status = ""
					
					# Convert the frame from OpenCV format to PyQt5 format
					frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
					convert_to_qt_format = QImage(
						frame.data, frame.shape[1],
						frame.shape[0],
						QImage.Format_RGB888)
					frame = convert_to_qt_format.scaled(720, 405, Qt.KeepAspectRatio)
					
					# Send the frames and Stats to the GUI window
					self.ImageUpdate.emit(frame)
					self.DrowsyStats.emit(drowsy_stats)
					self.YawnStats.emit(yawn_stats)
					self.Status.emit(status)
				
				except TypeError or ValueError or AttributeError or Exception:
					print("Trying to Read the footage!")
					pass
		# Close all opened windows and stop video Capture
		video_stream.release()
		cv.destroyAllWindows()
	
	# Thread stop method (De-Activate the thread and Quit the operation when method is called from GUI window)
	def stop(self):
		self.ThreadActive = False
		self.wait()
