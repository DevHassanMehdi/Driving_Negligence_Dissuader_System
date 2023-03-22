# PREP DEPENDENCIES
from PyQt5.QtCore import Qt, pyqtSignal, QThread  # To send out video frames to our PyQt5 GUI page
from PyQt5.QtGui import QImage  # To convert the OpenCV frames into PyQt5 image
import matplotlib.pyplot as plt  # For plotting and error checking
import edge_detection as edge  # Handles the detection of lane lines
from threading import Thread  # For multi-threading
import numpy as np  # For SCi-Calculations
import cv2 as cv  # For enabling computer vision
import warnings  # For dandelion the polyFit warnings
import os  # For System functions

# Ignoring the polyfit RankWarning
warnings.simplefilter('ignore', np.RankWarning)

# Video input source (Can be video or a camera)
input_video = 'dependencies/video/lds2.mp4'
# To use camera instead of video file, replace the above code with... input_video = 0

# Global variables
font = cv.FONT_HERSHEY_DUPLEX

prev_leftx = None
prev_lefty = None
prev_rightx = None
prev_righty = None
prev_left_fit = []
prev_right_fit = []

prev_leftx2 = None
prev_lefty2 = None
prev_rightx2 = None
prev_righty2 = None
prev_left_fit2 = []
prev_right_fit2 = []

LANE_THRESHOLD_LEFT = -150
LANE_THRESHOLD_RIGHT = 150
LANE_THRESH_COUNTER = 0
LANE_THRESHOLD = 20
lane_alert = False

speech = False

global output
global frame_with_lane_lines


# Alarm system
def generate_alert(center_offset):
	# If vehicles' center offset is outside threshold
	global LANE_THRESH_COUNTER
	global lane_alert
	if center_offset < LANE_THRESHOLD_LEFT or center_offset > LANE_THRESHOLD_RIGHT:
		# Increase counter
		LANE_THRESH_COUNTER += 1
		# If lane counter exceeds threshold
		if LANE_THRESH_COUNTER >= LANE_THRESHOLD:
			# Alert the driver
			if not lane_alert and not speech:
				lane_alert = True
				new_thread = Thread(target=alert)
				new_thread.deamon = True
				new_thread.start()
				return lane_alert
	# stop alert on lane fix
	else:
		LANE_THRESH_COUNTER = 0
		lane_alert = False


# Function to alarm the driver when skipping lane
def alert():
	global speech
	global lane_alert
	# When drowsy
	if lane_alert:
		speech = True
		speak = "afplay " + "dependencies/audio/stay-in-your-lane.mp3"
		os.system(speak)
		speech = False


# Class to represent a lane on the road
class Lane:
	curve_radius = ""
	curve_offset = ""
	
	# Default constructor. Takes original frame and set reign of interest points
	def __init__(self, orig_frame):
		
		self.orig_frame = orig_frame
		
		# variable to hold an image with the lane lines
		self.lane_line_markings = None
		
		# variables to hold the image after perspective transformation
		self.warped_frame = None
		self.transformation_matrix = None
		self.inv_transformation_matrix = None
		
		# (Width, Height) of the original video frame (or image)
		self.orig_image_size = self.orig_frame.shape[::-1][1:]
		
		width = self.orig_image_size[0]
		height = self.orig_image_size[1]
		self.width = width
		self.height = height
		
		if input_video == 'dependencies/video/lane1.mp4':
			# Set the reign of interest (for Lane1.mp4)
			self.roi_points = np.float32([
				(int(0.480 * width), int(0.635 * height)),  # Top-left corner
				(150, height - 15),  # Bottom-left corner
				(int(0.810 * width), height - 15),  # Bottom-right corner
				(int(0.535 * width), int(0.635 * height))  # Top-right corner
			])
		elif input_video == 'dependencies/video/lane2.mp4':
			# Set the reign of interest (for Lane2.mp4)
			self.roi_points = np.float32([
				(int(0.350 * width), int(0.500 * height)),  # Top-left corner
				(10, height - 1),  # Bottom-left corner
				(int(0.900 * width), height - 1),  # Bottom-right corner
				(int(0.650 * width), int(0.500 * height))  # Top-right corner
			])
		else:
			# Set the reign of interest
			self.roi_points = np.float32([
				(int(0.450 * width), int(0.610 * height)),  # Top-left corner
				(100, height - 1),  # Bottom-left corner
				(int(0.900 * width), height - 1),  # Bottom-right corner
				(int(0.550 * width), int(0.610 * height))  # Top-right corner
			])
		
		# The desired corner locations  of the region of interest after perspective transformation.
		self.padding = int(0.25 * width)  # padding from side of the image in pixels
		self.desired_roi_points = np.float32([
			[self.padding, 0],  # Top-left corner
			[self.padding, self.orig_image_size[1]],  # Bottom-left corner
			[self.orig_image_size[0] - self.padding, self.orig_image_size[1]],  # Bottom-right corner
			[self.orig_image_size[0] - self.padding, 0]  # Top-right corner
		])
		
		# Histogram that shows the white pixel peaks for lane line detection
		self.histogram = None
		
		# Sliding window parameters
		self.no_of_windows = 10
		self.margin = int((1 / 12) * width)  # Window width is +/- margin
		self.minpix = int((1 / 24) * width)  # Min no. of pixels to recenter window
		
		# Best fit polynomial lines for left line and right line of the lane
		self.left_fit = None
		self.right_fit = None
		self.left_lane_inds = None
		self.right_lane_inds = None
		self.ploty = None
		self.left_fitx = None
		self.right_fitx = None
		self.leftx = None
		self.rightx = None
		self.lefty = None
		self.righty = None
		
		# Pixel parameters for x and y dimensions
		self.YM_PER_PIX = 7.0 / 400  # meters per pixel in y dimension
		self.XM_PER_PIX = 3.7 / 255  # meters per pixel in x dimension
		
		# Radii of curvature and offset
		self.left_curvem = None
		self.right_curvem = None
		self.center_offset = None
	
	# Function to isolate the lane line edges in a frame
	def get_line_markings(self, frame=None):
		
		if frame is None:
			frame = self.orig_frame
		
		# Convert the video frame from BGR (blue, green, red) color space to HLS (hue, saturation, lightness).
		hls = cv.cvtColor(frame, cv.COLOR_BGR2HLS)
		
		# Isolate possible lane line edges
		# Perform Sobel edge detection on the L (lightness) channel
		_, sxbinary = edge.threshold(hls[:, :, 1], thresh=(120, 255))
		# Reduce noise
		sxbinary = edge.blur_gaussian(sxbinary, ksize=3)
		# Replace sobel values of lightness in thresh (110-255) to white (255) and the reset to black (0)
		sxbinary = edge.mag_thresh(sxbinary, sobel_kernel=3, thresh=(110, 255))
		
		# Perform binary thresholding on the S (saturation) channel
		# Replace binary values of saturation in thresh (110-255) to white (255) and the reset to black (0)
		_, s_binary = edge.threshold(hls[:, :, 2], (130, 255))
		
		# Perform binary thresholding on the R (red) channel
		_, r_thresh = edge.threshold(frame[:, :, 2], thresh=(120, 255))
		
		# use Bitwise AND operation to reduce noise and black-out any pixels with un-even HLS values
		rs_binary = cv.bitwise_and(s_binary, r_thresh)
		
		# Combine the possible lane lines with the possible lane line edges
		self.lane_line_markings = cv.bitwise_or(rs_binary, sxbinary.astype(np.uint8))
		return self.lane_line_markings, True
	
	# Function to perform perspective transformation on the frames
	def perspective_transform(self, frame=None):
		
		if frame is None:
			frame = self.lane_line_markings
		
		# Calculate the transformation matrix
		self.transformation_matrix = cv.getPerspectiveTransform(
			self.roi_points, self.desired_roi_points)
		
		# Calculate the inverse transformation matrix
		self.inv_transformation_matrix = cv.getPerspectiveTransform(
			self.desired_roi_points, self.roi_points)
		
		# Perform the transform using the transformation matrix
		self.warped_frame = cv.warpPerspective(
			frame, self.transformation_matrix, self.orig_image_size, flags=(
				cv.INTER_LINEAR))
		
		# Convert image to binary
		(thresh, binary_warped) = cv.threshold(
			self.warped_frame, 127, 255, cv.THRESH_BINARY)
		self.warped_frame = binary_warped
		
		return self.warped_frame, True
	
	# Function to calculate image histogram to find peaks in white pixel count
	def calculate_histogram(self, frame=None, plot=True):
		
		if frame is None:
			frame = self.warped_frame
		
		# Generate the histogram
		self.histogram = np.sum(frame[int(
			frame.shape[0] / 2):, :], axis=0)
		
		if plot:
			# Draw both the image and the histogram
			figure, (ax1, ax2) = plt.subplots(2, 1)  # 2 row, 1 columns
			figure.set_size_inches(10, 5)
			ax1.imshow(frame, cmap='gray')
			ax1.set_title("Warped Binary Frame")
			ax2.plot(self.histogram)
			ax2.set_title("Histogram Peaks")
			plt.show()
		
		return self.histogram, True
	
	# Function to get the left and right peak of the histogram
	def histogram_peak(self):
		
		midpoint = int(self.histogram.shape[0] / 2)
		leftx_base = np.argmax(self.histogram[:midpoint])
		rightx_base = np.argmax(self.histogram[midpoint:]) + midpoint
		
		# (x coordinate of left peak, x coordinate of right peak)
		return leftx_base, rightx_base
	
	# Function to get the indices of the lane line pixels using the sliding windows technique
	def get_lane_line_indices_sliding_windows(self):
		
		# Sliding window width is +/- margin
		margin = self.margin
		
		frame_sliding_window = self.warped_frame.copy()
		
		# Set the height of the sliding windows
		window_height = int(self.warped_frame.shape[0] / self.no_of_windows)
		
		# Find the x and y coordinates of all the nonzero
		# (i.e. white) pixels in the frame.
		nonzero = self.warped_frame.nonzero()
		nonzeroy = np.array(nonzero[0])
		nonzerox = np.array(nonzero[1])
		
		# Store the pixel indices for the left and right lane lines
		left_lane_inds = []
		right_lane_inds = []
		
		# Current positions for pixel indices for each window which we will continue to update
		leftx_base, rightx_base = self.histogram_peak()
		leftx_current = leftx_base
		rightx_current = rightx_base
		
		# Go through one window at a time
		no_of_windows = self.no_of_windows
		
		for window in range(no_of_windows):
			
			# Identify window boundaries in x and y (and right and left)
			win_y_low = self.warped_frame.shape[0] - (window + 1) * window_height
			win_y_high = self.warped_frame.shape[0] - window * window_height
			win_xleft_low = leftx_current - margin
			win_xleft_high = leftx_current + margin
			win_xright_low = rightx_current - margin
			win_xright_high = rightx_current + margin
			cv.rectangle(frame_sliding_window, (win_xleft_low, win_y_low), (
				win_xleft_high, win_y_high), (255, 255, 255), 2)
			cv.rectangle(frame_sliding_window, (win_xright_low, win_y_low), (
				win_xright_high, win_y_high), (255, 255, 255), 2)
			
			# Identify the nonzero pixels in x and y within the window
			good_left_inds = (
					(nonzeroy >= win_y_low) &
					(nonzeroy < win_y_high) &
					(nonzerox >= win_xleft_low) &
					(nonzerox < win_xleft_high)).nonzero()[0]
			good_right_inds = (
					(nonzeroy >= win_y_low) &
					(nonzeroy < win_y_high) &
					(nonzerox >= win_xright_low) &
					(nonzerox < win_xright_high)).nonzero()[0]
			
			# Append these indices to the lists
			left_lane_inds.append(good_left_inds)
			right_lane_inds.append(good_right_inds)
			
			# If you found > minpix pixels, recenter next window on mean position
			minpix = self.minpix
			if len(good_left_inds) > minpix:
				leftx_current = int(np.mean(nonzerox[good_left_inds]))
			if len(good_right_inds) > minpix:
				rightx_current = int(np.mean(nonzerox[good_right_inds]))
		
		# Concatenate the arrays of indices
		left_lane_inds = np.concatenate(left_lane_inds)
		right_lane_inds = np.concatenate(right_lane_inds)
		
		# Extract the pixel coordinates for the left and right lane lines
		leftx = nonzerox[left_lane_inds]
		lefty = nonzeroy[left_lane_inds]
		rightx = nonzerox[right_lane_inds]
		righty = nonzeroy[right_lane_inds]
		
		# Fit a second order polynomial curve to the pixel coordinates for the left and right lane lines
		
		global prev_leftx
		global prev_lefty
		global prev_rightx
		global prev_righty
		global prev_left_fit
		global prev_right_fit
		
		# Make sure we have nonzero pixels
		if len(leftx) == 0 or len(lefty) == 0 or len(rightx) == 0 or len(righty) == 0:
			leftx = prev_leftx
			lefty = prev_lefty
			rightx = prev_rightx
			righty = prev_righty
		
		left_fit = np.polyfit(lefty, leftx, 2)
		right_fit = np.polyfit(righty, rightx, 2)
		
		# Add the latest polynomial coefficients
		prev_left_fit.append(left_fit)
		prev_right_fit.append(right_fit)
		
		# Calculate the moving average
		if len(prev_left_fit) > 10:
			prev_left_fit.pop(0)
			prev_right_fit.pop(0)
			left_fit = sum(prev_left_fit) / len(prev_left_fit)
			right_fit = sum(prev_right_fit) / len(prev_right_fit)
		
		self.left_fit = left_fit
		self.right_fit = right_fit
		
		prev_leftx = leftx
		prev_lefty = lefty
		prev_rightx = rightx
		prev_righty = righty
		
		return self.left_fit, self.right_fit
	
	# Function to use the lane line from the previous sliding window to get the parameters
	def get_lane_line_previous_window(self, left_fit, right_fit, plot=False):
		
		# margin is a sliding window parameter
		margin = self.margin
		
		# Find the x and y coordinates of all the nonzero
		# (i.e. white) pixels in the frame.
		nonzero = self.warped_frame.nonzero()
		nonzeroy = np.array(nonzero[0])
		nonzerox = np.array(nonzero[1])
		
		# Store left and right lane pixel indices
		left_lane_indices = (
				(nonzerox > (left_fit[0] * (nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] - margin)) &
				(nonzerox < (left_fit[0] * (nonzeroy ** 2) + left_fit[1] * nonzeroy + left_fit[2] + margin)))
		right_lane_indices = (
				(nonzerox > (right_fit[0] * (nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] - margin)) &
				(nonzerox < (right_fit[0] * (nonzeroy ** 2) + right_fit[1] * nonzeroy + right_fit[2] + margin)))
		
		self.left_lane_inds = left_lane_indices
		self.right_lane_inds = right_lane_indices
		
		# Get the left and right lane line pixel locations
		leftx = nonzerox[left_lane_indices]
		lefty = nonzeroy[left_lane_indices]
		rightx = nonzerox[right_lane_indices]
		righty = nonzeroy[right_lane_indices]
		
		global prev_leftx2
		global prev_lefty2
		global prev_rightx2
		global prev_righty2
		global prev_left_fit2
		global prev_right_fit2
		
		# Make sure we have nonzero pixels
		if len(leftx) == 0 or len(lefty) == 0 or len(rightx) == 0 or len(righty) == 0:
			leftx = prev_leftx2
			lefty = prev_lefty2
			rightx = prev_rightx2
			righty = prev_righty2
		
		self.leftx = leftx
		self.rightx = rightx
		self.lefty = lefty
		self.righty = righty
		
		left_fit = np.polyfit(lefty, leftx, 2)
		right_fit = np.polyfit(righty, rightx, 2)
		
		# Add the latest polynomial coefficients
		prev_left_fit2.append(left_fit)
		prev_right_fit2.append(right_fit)
		
		# Calculate the moving average
		if len(prev_left_fit2) > 10:
			prev_left_fit2.pop(0)
			prev_right_fit2.pop(0)
			left_fit = sum(prev_left_fit2) / len(prev_left_fit2)
			right_fit = sum(prev_right_fit2) / len(prev_right_fit2)
		
		self.left_fit = left_fit
		self.right_fit = right_fit
		
		prev_leftx2 = leftx
		prev_lefty2 = lefty
		prev_rightx2 = rightx
		prev_righty2 = righty
		
		# Create the x and y values to plot on the image
		ploty = np.linspace(
			0, self.warped_frame.shape[0] - 1, self.warped_frame.shape[0])
		left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
		right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]
		self.ploty = ploty
		self.left_fitx = left_fitx
		self.right_fitx = right_fitx
		
		if plot:
			# Generate images to draw on
			out_img = np.dstack((self.warped_frame, self.warped_frame, (
				self.warped_frame))) * 255
			window_img = np.zeros_like(out_img)
			
			# Add color to the left and right line pixels
			out_img[nonzeroy[left_lane_indices], nonzerox[left_lane_indices]] = [255, 0, 0]
			out_img[nonzeroy[right_lane_indices], nonzerox[right_lane_indices]] = [
				0, 0, 255]
			
			# Create a polygon to show the search window area, and recast
			# the x and y points into a usable format for cv.fillPoly()
			margin = self.margin
			left_line_window1 = np.array([np.transpose(np.vstack([
				left_fitx - margin, ploty]))])
			left_line_window2 = np.array([np.flipud(np.transpose(np.vstack([
				left_fitx + margin, ploty])))])
			left_line_pts = np.hstack((left_line_window1, left_line_window2))
			right_line_window1 = np.array([np.transpose(np.vstack([
				right_fitx - margin, ploty]))])
			right_line_window2 = np.array([np.flipud(np.transpose(np.vstack([
				right_fitx + margin, ploty])))])
			right_line_pts = np.hstack((right_line_window1, right_line_window2))
			
			# Draw the lane onto the warped blank image
			cv.fillPoly(window_img, np.int_([left_line_pts]), (0, 255, 0))
			cv.fillPoly(window_img, np.int_([right_line_pts]), (0, 255, 0))
			result = cv.addWeighted(out_img, 1, window_img, 0.3, 0)
			
			# Plot the figures
			figure, (ax1, ax2, ax3) = plt.subplots(3, 1)  # 3 rows, 1 column
			figure.set_size_inches(10, 10)
			figure.tight_layout(pad=3.0)
			ax1.imshow(cv.cvtColor(self.orig_frame, cv.COLOR_BGR2RGB))
			ax2.imshow(self.warped_frame, cmap='gray')
			ax3.imshow(result)
			ax3.plot(left_fitx, ploty, color='yellow')
			ax3.plot(right_fitx, ploty, color='yellow')
			ax1.set_title("Original Frame")
			ax2.set_title("Warped Frame")
			ax3.set_title("Warped Frame With Search Window")
			plt.show()
	
	# Function to overlay the lane lines onto original frame
	def overlay_lane_lines(self, plot=False):
		
		# Generate an image to draw the lane lines on
		warp_zero = np.zeros_like(self.warped_frame).astype(np.uint8)
		color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
		
		# Recast the x and y points into usable format for cv.fillPoly()
		pts_left = np.array([np.transpose(np.vstack([
			self.left_fitx, self.ploty]))])
		pts_right = np.array([np.flipud(np.transpose(np.vstack([
			self.right_fitx, self.ploty])))])
		pts = np.hstack((pts_left, pts_right))
		
		# Draw lane on the warped blank image
		cv.fillPoly(color_warp, np.int_([pts]), (255, 255, 255))
		
		# Warp the blank back to original image space using inverse perspective matrix (Minv)
		newwarp = cv.warpPerspective(
			color_warp,
			self.inv_transformation_matrix, (
				self.orig_frame.shape[1],
				self.orig_frame.shape[0]))
		
		# Combine the result with the original image
		result = cv.addWeighted(self.orig_frame, 1, newwarp, 0.3, 0)
		
		if plot:
			# Plot the figures
			figure, (ax1, ax2) = plt.subplots(2, 1)  # 2 rows, 1 column
			figure.set_size_inches(10, 10)
			figure.tight_layout(pad=3.0)
			ax1.imshow(cv.cvtColor(self.orig_frame, cv.COLOR_BGR2RGB))
			ax2.imshow(cv.cvtColor(result, cv.COLOR_BGR2RGB))
			ax1.set_title("Original Frame")
			ax2.set_title("Original Frame With Lane Overlay")
			plt.show()
		
		return result, True
	
	# Function to calculate curvature of the lane
	def calculate_curvature(self, print_to_terminal=False):
		
		# Set the y-value where we want to calculate the road curvature.
		# Select the maximum y-value, which is the bottom of the frame.
		y_eval = np.max(self.ploty)
		
		# Fit polynomial curves to the real world environment
		left_fit_cr = np.polyfit(self.lefty * self.YM_PER_PIX, self.leftx * (
			self.XM_PER_PIX), 2)
		right_fit_cr = np.polyfit(self.righty * self.YM_PER_PIX, self.rightx * (
			self.XM_PER_PIX), 2)
		
		# Calculate the radii of curvature
		left_curvem = (
							(1 + (2 * left_fit_cr[0] * y_eval * self.YM_PER_PIX + left_fit_cr[1]) ** 2)
							** 1.5) / np.absolute(2 * left_fit_cr[0])
		right_curvem = (
							(1 + (2 * right_fit_cr[0] * y_eval * self.YM_PER_PIX + right_fit_cr[1]) ** 2)
							** 1.5) / np.absolute(2 * right_fit_cr[0])
		
		# Display on terminal window
		if print_to_terminal:
			print(left_curvem, 'm', right_curvem, 'm')
		
		self.left_curvem = left_curvem
		self.right_curvem = right_curvem
		
		return left_curvem, right_curvem
	
	# Function to calculate the center of offset of the vehicle from the lane
	def calculate_car_position(self, print_to_terminal=False):
		
		# Assume the camera is centered in the image.
		# Get position of car in centimeters
		car_location = self.orig_frame.shape[1] / 2
		
		# Fine the x coordinate of the lane line bottom
		height = self.orig_frame.shape[0]
		bottom_left = self.left_fit[0] * height ** 2 + self.left_fit[
			1] * height + self.left_fit[2]
		bottom_right = self.right_fit[0] * height ** 2 + self.right_fit[
			1] * height + self.right_fit[2]
		
		center_lane = (bottom_right - bottom_left) / 2 + bottom_left
		center_offset = (np.abs(car_location) - np.abs(
			center_lane)) * self.XM_PER_PIX * 100
		
		if print_to_terminal:
			print(str(center_offset) + 'cm')
		
		self.center_offset = center_offset
		return center_offset
	
	# Function to plot curvature and offset statistics on the image
	def display_curvature_offset(self, frame=None, plot=False):
		
		if frame is None:
			image_copy = self.orig_frame.copy()
		else:
			image_copy = frame
		
		# Show the image at this stage if plot is true
		if plot:
			cv.imshow("Image with Curvature and Offset", image_copy)
		
		return image_copy
	
	# Function to send Curve radios value in string to thread class
	def calculate_curve_radius(self):
		curve_radius = f"Curve Radius: {round(((self.left_curvem + self.right_curvem) / 2), 1)}"
		return curve_radius
	
	# Function to send Curve Offset value in string to thread class
	def calculate_curve_offset(self):
		curve_offset = f"Curve Offset: {round(self.center_offset, 1)}"
		return curve_offset


# Lane Detection Thread class (The LDS will run in a separate thread when called by the start button from GUI page)
class StartLDS(QThread):
	# Variable that will be sent to GUI page
	ImageUpdate = pyqtSignal(QImage)
	CurveRadius = pyqtSignal(str)
	CurveOffset = pyqtSignal(str)
	Status = pyqtSignal(str)
	
	def __init__(self):
		super().__init__()
		self.ThreadActive = None
	
	# Lane Detection begins here (The method will run when the thread starts)
	def run(self):
		# Activating thread
		self.ThreadActive = True
		global output
		global frame_with_lane_lines
		# Start the video stream
		video_stream = cv.VideoCapture(input_video)
		
		# Process the video
		while self.ThreadActive:
			# Set the FPS cap on video
			cv.waitKey(5)
			# Split video into frames
			ret, frame = video_stream.read()
			if ret:
				# Resize the frame
				frame = cv.resize(frame, (560, 315))
				# Store the original frame
				original_frame = frame.copy()
				try:
					# Create a Lane object
					lane_obj = Lane(orig_frame=original_frame)
					# Perform thresholding to isolate lane lines
					lane_obj.get_line_markings()
					# Perform the perspective transform to generate a bird's eye view
					lane_obj.perspective_transform()
					# Generate the image histogram to serve as a starting point for finding lane line pixels
					lane_obj.calculate_histogram(plot=False)
					# Find lane line pixels using the sliding window method
					left_fit, right_fit = lane_obj.get_lane_line_indices_sliding_windows()
					# Fill in the lane line
					lane_obj.get_lane_line_previous_window(left_fit, right_fit, plot=False)
					# Overlay lines on the original frame
					frame_with_lane_lines = lane_obj.overlay_lane_lines(plot=False)[0]
					# Calculate lane line curvature (left and right lane lines)
					lane_obj.calculate_curvature(print_to_terminal=False)
					# Calculate center offset
					lane_obj.calculate_car_position(print_to_terminal=False)
					# Generate Alert
					generate_alert(lane_obj.calculate_car_position(print_to_terminal=False))
					# Set the curve radius value string that wil be sent to the GUI frame
					curve_radius = lane_obj.calculate_curve_radius()
					# Set the curve offset value string that wil be sent to the GUI frame
					curve_offset = lane_obj.calculate_curve_offset()
					# Set the alert status that wil be sent to the GUI frame
					if lane_alert:
						status = "Stay In Your Lane!"
					else:
						status = ""
					# Convert the frame from OpenCV format to PyQt5 format
					frame = cv.cvtColor(frame_with_lane_lines, cv.COLOR_BGR2RGB)
					convert_to_qt_format = QImage(
						frame.data, frame.shape[1],
						frame.shape[0],
						QImage.Format_RGB888)
					frame = convert_to_qt_format.scaled(720, 405, Qt.KeepAspectRatio)
					
					# # Send the frames and Stats to the GUI page
					self.ImageUpdate.emit(frame)
					self.CurveRadius.emit(curve_radius)
					self.CurveOffset.emit(curve_offset)
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
