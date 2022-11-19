import cv2 as cv  # For enabling computer vision
import numpy as np  # For SCi-Calculations


# Detect edges using thresholding and sobel transformation

# Takes image returns Black n white threshold image
def binary_array(array, thresh, value=0):
	if value == 0:
		# Create an array of ones with the same shape and type as
		# the input 2D array.
		binary = np.ones_like(array)
	
	else:
		# Creates an array of zeros with the same shape and type as
		# the input 2D array.
		binary = np.zeros_like(array)
		value = 1
	
	binary[(array >= thresh[0]) & (array <= thresh[1])] = value
	
	return binary


# Takes noisy Image, apply Gaussian blur to remove noise of the image and returns it
def blur_gaussian(channel, ksize=3):
	return cv.GaussianBlur(channel, (ksize, ksize), 0)


# Takes image, applies sobel edge detection to detect sharp edges and returns it
def mag_thresh(image, sobel_kernel=3, thresh=(0, 255)):
	# Get the magnitude of the edges that are vertically aligned on the image
	sobelx = np.absolute(sobel(image, orient='x', sobel_kernel=sobel_kernel))
	
	# Get the magnitude of the edges that are horizontally aligned on the image
	sobely = np.absolute(sobel(image, orient='y', sobel_kernel=sobel_kernel))
	
	# Find areas of the image that have the strongest pixel intensity changes
	mag = np.sqrt(sobelx ** 2 + sobely ** 2)
	
	# Return image that contains 0s and 1s
	return binary_array(mag, thresh)


global _sobel


# Sobel's transformation method
def sobel(img_channel, orient='x', sobel_kernel=3):
	global _sobel
	if orient == 'x':
		_sobel = cv.Sobel(img_channel, cv.CV_64F, 1, 0, sobel_kernel)
	if orient == 'y':
		# Will detect differences in pixel intensities going from top to bottom on the image
		_sobel = cv.Sobel(img_channel, cv.CV_64F, 0, 1, sobel_kernel)
	
	return _sobel


# Takes image, apply binary thresholding and returns it
def threshold(channel, thresh=(128, 255), thresh_type=cv.THRESH_BINARY):
	# If pixel intensity is greater than thresh[0], make that value white (255), else set it to black (0)
	return cv.threshold(channel, thresh[0], thresh[1], thresh_type)
