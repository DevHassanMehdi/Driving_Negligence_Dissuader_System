# PREP DEPENDENCIES
from drowsy_yawn_detection import StartDDS  # Drowsiness detection system
from pedestrian_detection import StartPDS  # Pedestrian detection system
from object_detection import StartODS  # Object Detection System
from lane_detection import StartLDS  # Lane Detection System
from functools import partial  # To send args with connect command
# PyQt5 items for our GUI application
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
# Misc Dependencies
import darkdetect  # To set application theme according to the operating system
import sys  # For system functions
import os  # For OS functions

# Dictionary to store all the widgets of the GUI application
widgets = {
	"header": [],
	"footer": [],
	"start_dds": [],
	"start_lds": [],
	"start_ods": [],
	"start_pds": [],
	"start_dnds": [],
	"close_reset_dnds": [],
	"theme_change": [],
	"show_mar_dds": [],
	"show_ear_dds": [],
	"stop_button_dds": [],
	"stop_button_lds": [],
	"stop_button_ods": [],
	"stop_button_pds": [],
	"stop_button_dnds": [],
	"video_feed_dds": [],
	"video_feed_lds": [],
	"video_feed_ods": [],
	"video_feed_pds": [],
	"show_curve_radius_lds": [],
	"show_curve_offset_lds": [],
	"status_update_dds": [],
	"status_update_lds": [],
	"show_detection_stats_ods": [],
	"show_detection_stats_pds": []}

# Stylesheet for light mode
light_style = """
	*{
		color: #7F7F7F;}
		
	#centralwidget{
		background: #F0EBEB;
		border-radius: 20%;}
	
	#button{
		color: #CCCCCC;
		border: 1px solid #FF1937;
		background: #372D2D;
		border-radius : 30%;
		font-size: 20px;
		width: 50px;
		height: 50px;
		padding: 5%;
		margin: 15%;}
		
	#button:hover{
		background: #AF0F23;
		border: 1px solid #343030;}
	
	#label{
		font-size: 20px;
		border-radius: 10%;}
	
	#header{
		font-weight: bold;
		font-size: 48px;
		margin-top: 5%}

	#close_reset_button{
		background: #F0EBEB;
		font-size: 20px;
		font-weight: bold;
		border-radius : 12px;
		padding: 1%;}
		
	#close_reset_button:hover{
		color: #CCCCCC;
		background: #AF0F23;
		border: 1px solid #343030;}
	
	#theme_change{
		background: url(dependencies/images/sun.png) repeat-x left top;
		font-size: 20px;
		font-weight: bold;
		border-radius : 16px;
		padding: 1%;}

	#theme_change:hover{
		background: url(dependencies/images/moon.png) repeat-x left top;}
	
	#footer{
		font-size: 14px;
		margin-bottom: 5%}
		
		/* This is the end of light stylesheet */"""

# Stylesheet for dark mode
dark_style = """
	*{
		color: #B3B3B3;}
		
	#centralwidget{
		background: #282323;
		border-radius: 20%;}
	
	#button{
		color: #cccccc;
		border: 1px solid #7D0A19;
		background: #191414;
		font-size: 20px;
		border-radius : 30%;
		width: 50px;
		height: 50px;
		padding: 5%;
		margin: 15%;}

	#button:hover{
		background: #7D0A19;
		border: 1px solid #343030;}

	#label{
		font-size: 20px;
		border-radius: 30%;}

	#header{
		font-weight: bold;
		font-size: 48px;
		margin-top: 5%}

	#close_reset_button{
		background: #191414;
		font-size: 20px;
		font-weight: bold;
		border-radius : 12px;
		padding: 1%;}

	#close_reset_button:hover{
		background: #7D0A19;
		border: 1px solid #343030;}
	
	#theme_change{
		background: url(dependencies/images/moon.png) repeat-x left top;
		font-size: 20px;
		font-weight: bold;
		border-radius : 16px;
		padding: 1%;}

	#theme_change:hover{
		background: url(dependencies/images/sun.png) repeat-x left top;}
		
	#footer{
		font-size: 14px;
		margin-bottom: 5%}
		
		/* This is the end of dark stylesheet */"""


# Driving Negligence Dissuader System main class
class DNDS(QWidget):
	# Methods to move the frameless window upon drag
	def mousePressEvent(self, event):
		self.old_position = event.globalPos()
	
	# Grab old position from mousePressEvent and move the window as th mouse drags it
	def mouseMoveEvent(self, event):
		movement = QPoint(event.globalPos() - self.old_position)
		self.move(self.x() + movement.x(), self.y() + movement.y())
		self.old_position = event.globalPos()
	
	# Method to center the window frame
	def center(self):
		geometry = self.frameGeometry()
		screen_center_point = QDesktopWidget().availableGeometry().center()
		geometry.moveCenter(screen_center_point)
		self.move(geometry.topLeft())
	
	# The Init Methods
	def __init__(self, *args, **kwargs):
		super(DNDS, self).__init__(*args, **kwargs)
		# Current window position
		self.old_position = None
		# Layout and window settings
		grid = QGridLayout()
		grid.setSpacing(10)
		self.setFont(QFont("Nunito"))
		self.centralwidget = QWidget(self)
		self.centralwidget.resize(850, 650)
		self.centralwidget.setObjectName("centralwidget")
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setWindowFlag(Qt.FramelessWindowHint)
		self.setWindowOpacity(0.99)
		self.setLayout(grid)
		self.center()
		
		# Method to change application theme
		def change_theme_stylesheet():
			# If current style is light, change it to dark
			if self.styleSheet() == light_style:
				self.setStyleSheet(dark_style)
			# If current style is dark, change it to light
			elif self.styleSheet() == dark_style:
				self.setStyleSheet(light_style)
		
		# If te application has no stylesheet, set the default stylesheet
		if self.styleSheet() == "":
			# if system theme is Light, set light stylesheet
			if darkdetect.isLight():
				self.setStyleSheet(light_style)
			# if system theme is Dark, set Dark stylesheet
			elif darkdetect.isDark():
				self.setStyleSheet(dark_style)
			# if system theme is not recognized, set light stylesheet
			else:
				self.setStyleSheet(light_style)
		
		# Make video frame corners round
		def make_frame_rounded(widget, video_frame, antialiasing=False):
			# set Min Max size for video label widget
			widget.setMaximumSize(widget.width(), widget.height())
			widget.setMinimumSize(widget.width(), widget.height())
			# Roundness of the corners
			radius = 20
			# The final frame that is to be set onto the Qlabel
			final_rounded_frame = QPixmap(widget.size())
			final_rounded_frame.fill(Qt.transparent)
			# Scale the input frame according to the label dimensions
			frame = QPixmap(video_frame).scaled(
				widget.width(), widget.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
			# Painter to paint the rounded rectangle onto the final frame
			painter = QPainter(final_rounded_frame)
			# If Antialiasing is On, make the rounded corners smoother
			if antialiasing:
				painter.setRenderHint(QPainter.Antialiasing, True)
				painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
				painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
			# Paint the frame
			path = QPainterPath()
			path.addRoundedRect(10, 10, widget.width() - 15, widget.height() - 15, radius, radius)
			painter.setClipPath(path)
			painter.drawPixmap(0, 0, frame)
			# Set the painted frames ont the Qlabel widget
			widget.setPixmap(final_rounded_frame)
			# terminate the painter
			painter.end()
			# Return the widget
			return widget
		
		# Call clear widgets method and switch to the called page
		def start_operation(operation_id):
			clear_widgets()
			
			if operation_id == "HOME":
				self.setFixedSize(850, 650)
				home_page()
			if operation_id == "DDS":
				self.setFixedSize(850, 650)
				page_dds(return_items=False)
			if operation_id == "LDS":
				self.setFixedSize(850, 650)
				page_lds(return_items=False)
			if operation_id == "ODS":
				self.setFixedSize(850, 650)
				page_ods(return_items=False)
			if operation_id == "PDS":
				self.setFixedSize(850, 650)
				page_pds(return_items=False)
			if operation_id == "DNDS":
				self.setFixedSize(1200, 850)
				self.center()
				page_dnds()
			
			# Resize central widget
			self.centralwidget.resize(self.width(), self.height())
		
		# Method to Close/reset DNDS
		def close_operation():
			# Confirmation box asking user if they want to close or Reset DNDS
			confirm_close_reset = QMessageBox()
			# confirmation box styling
			confirm_close_reset.setStyleSheet("""
					*{	color: #CCCCCC;
						background: #231E1E;}
					QLabel{
						font-size: 16px;}
					QPushButton{
						color:#CCCCCC;
						padding:5px;
						font-size: 14px;
						border-radius:13px;
						background: #191414;}
					QPushButton:hover{
						background: #AF0F23;}""")
			confirm_close_reset.setWindowOpacity(0.95)
			confirm_close_reset.setText("Thank you for using DNDS.")
			confirm_close_reset.setStandardButtons(QMessageBox.Cancel | QMessageBox.Close | QMessageBox.Reset)
			confirm_close_reset = confirm_close_reset.exec()
			# If user confirms close then exit app
			if confirm_close_reset == QMessageBox.Close:
				sys.exit()
			# If user confirms reset then restart app
			elif confirm_close_reset == QMessageBox.Reset:
				os.execl(sys.executable, sys.executable, *sys.argv)
			# Else cancel
			else:
				pass
		
		# Methods to clear all the widgets in current page when switching to another page
		def clear_widgets():
			for widget in widgets:
				if widgets[widget]:
					widgets[widget][-1].hide()
					grid.removeWidget(widgets[widget][-1])
				for i in range(0, len(widgets[widget])):
					widgets[widget].pop()
		
		# Method to create button with pre-set stylesheet
		def create_button(button_text):
			# Create button
			button = QPushButton(button_text)
			button.setObjectName("button")
			# Change cursor to Pointing hand upon hover
			button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
			# Creating shadow object
			shadow = QGraphicsDropShadowEffect()
			# setting blur radius (optional step)
			shadow.setBlurRadius(10)
			shadow.setColor(QColor(65, 65, 65, 100))
			shadow.setOffset(2.5, 7.5)
			button.setGraphicsEffect(shadow)
			# Return the button
			return button
		
		# Method to create labels with pre-set stylesheet
		def create_label():
			# Create label
			label = QLabel()
			label.setObjectName("label")
			label.setAlignment(QtCore.Qt.AlignCenter)
			# Return the label
			return label
		
		# Drowsiness Detection System page
		def page_dds(return_items):
			# Update the video stream constantly while receiving frames from the drowsy_yawn_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				make_frame_rounded(video_feed_dds, frame, antialiasing=False)
			
			# Update the Eye Aspect Ratio constantly while receiving data from the drowsy_yawn_detection.py file
			def ear_update(drowsy_stats):
				show_ear.setText(drowsy_stats)
			
			# Update the Mouth Aspect Ratio stream constantly while receiving data from the drowsy_yawn_detection.py file
			def mar_update(yawn_stats):
				show_mar.setText(yawn_stats)
			
			# Update and show the Drowsy or Yawning
			def status_update(status):
				status_update_dds.setText(status)
			
			# Method to stop the Drowsiness detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				start_operation("HOME")
				drowsiness_detection_system.stop()
			
			try:
				# Create a label to display video on top of it
				video_feed_dds = QLabel()
				widgets["video_feed_dds"].append(video_feed_dds)
				#
				# Create a thread using DDS thread class and start the thread thereby starting DDS
				drowsiness_detection_system = StartDDS()
				drowsiness_detection_system.start()
				# Set the incoming video from the drowsy_yawn_detection.py on top of the label
				drowsiness_detection_system.ImageUpdate.connect(video_stream_update)
				
				# Create label to show EAR and Drowsy Count
				show_ear = create_label()
				widgets["show_ear_dds"].append(show_ear)
				# Set the incoming string from the drowsy_yawn_detection.py on top of the label
				drowsiness_detection_system.DrowsyStats.connect(ear_update)
				
				# Create label to show MAR and Yawn Count
				show_mar = create_label()
				widgets["show_mar_dds"].append(show_mar)
				# Set the incoming string from the drowsy_yawn_detection.py on top of the label
				drowsiness_detection_system.YawnStats.connect(mar_update)
				
				# Create label to show drowsy or yawning status
				status_update_dds = create_label()
				widgets["status_update_dds"].append(status_update_dds)
				# Set the incoming string from the drowsy_yawn_detection.py on top of the label
				drowsiness_detection_system.Status.connect(status_update)
				
				# Create stop button that will call the stop_operation method
				stop_button_dds = create_button("Stop")
				stop_button_dds.clicked.connect(stop_operation)
				widgets["stop_button_dds"].append(stop_button_dds)
				
				# Return the widgets to DNDS page is the call came from DNDS page
				if return_items:
					# Set Frame size according to the window
					video_feed_dds.setFixedSize(560, 315)
					return drowsiness_detection_system
				# Display the widgets in separate page
				else:
					# Set Frame size according to the window
					video_feed_dds.setFixedSize(800, 450)
					
					# place widgets on the grid
					grid.addWidget(widgets["show_ear_dds"][-1], 0, 0, 1, 2)
					grid.addWidget(widgets["show_mar_dds"][-1], 0, 2, 1, 2)
					grid.addWidget(widgets["video_feed_dds"][-1], 1, 0, 1, 4)
					grid.addWidget(widgets["status_update_dds"][-1], 2, 0, 1, 4)
					grid.addWidget(widgets["stop_button_dds"][-1], 3, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError or Exception:
				start_operation("HOME")
		
		# Lane Detection System page
		def page_lds(return_items):
			# Update the video stream constantly while receiving frames from the lane_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				make_frame_rounded(video_feed_lds, frame, antialiasing=False)
			
			# Update the curve radius value constantly while receiving data from the lane_detection.py file
			def curve_radius_update(curve_radius):
				show_curve_radius.setText(curve_radius)
			
			# Update the curve offset value constantly while receiving data from the lane_detection.py file
			def curve_offset_update(curve_offset):
				show_curve_offset.setText(curve_offset)
			
			# Update and show the lane warning when moving outside the lane
			def status_update(status):
				status_update_lds.setText(status)
			
			# Method to stop the Lane detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				start_operation("HOME")
				lane_detection_system.stop()
			
			try:
				# Create a label to display video on top of it
				video_feed_lds = create_label()
				widgets["video_feed_lds"].append(video_feed_lds)
				
				# Create a thread using LDS thread class and start the thread thereby starting LDS
				lane_detection_system = StartLDS()
				lane_detection_system.start()
				# Set the incoming video from the lane_detection.py on top of the label
				lane_detection_system.ImageUpdate.connect(video_stream_update)
				
				# Create label to show curve radius
				show_curve_radius = create_label()
				widgets["show_curve_radius_lds"].append(show_curve_radius)
				# Set the incoming string from the lane_detection.py on top of the label
				lane_detection_system.CurveRadius.connect(curve_radius_update)
				
				# Create label to show curve offset
				show_curve_offset = create_label()
				widgets["show_curve_offset_lds"].append(show_curve_offset)
				# Set the incoming string from the lane_detection.py on top of the label
				lane_detection_system.CurveOffset.connect(curve_offset_update)
				
				# Create label to show lane status
				status_update_lds = create_label()
				widgets["status_update_lds"].append(status_update_lds)
				# Set the incoming string from the lane_detection.py on top of the label
				lane_detection_system.Status.connect(status_update)
				
				# Create stop button that will call the stop_operation method
				stop_button_lds = create_button("Stop")
				stop_button_lds.clicked.connect(stop_operation)
				widgets["stop_button_lds"].append(stop_button_lds)
				
				# Return the widgets to DNDS page is the call came from DNDS page
				if return_items:
					# Set Frame size according to the window
					video_feed_lds.setFixedSize(560, 315)
					return lane_detection_system
				# Show the widgets in a separate page
				else:
					# Set Frame size according to the window
					video_feed_lds.setFixedSize(800, 450)
					grid.addWidget(widgets["show_curve_radius_lds"][-1], 0, 0, 1, 2)
					grid.addWidget(widgets["show_curve_offset_lds"][-1], 0, 2, 1, 2)
					grid.addWidget(widgets["video_feed_lds"][-1], 1, 0, 1, 4)
					grid.addWidget(widgets["status_update_lds"][-1], 2, 0, 1, 4)
					grid.addWidget(widgets["stop_button_lds"][-1], 3, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError or Exception:
				start_operation("HOME")
		
		# Object Detection System page
		def page_ods(return_items):
			# Update the video stream constantly while receiving frames from the object_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				make_frame_rounded(video_feed_ods, frame, antialiasing=False)
			
			# Update the detection stats constantly while receiving data from the object_detection.py file
			def detection_stats_update(stats):
				show_detection_stats.setText(stats)
			
			# Method to stop the object detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				start_operation("HOME")
				object_detection_system.stop()
			
			try:
				# Create a label to display video on top of it
				video_feed_ods = create_label()
				widgets["video_feed_ods"].append(video_feed_ods)
				
				# Create a thread using ODS thread class and start the thread thereby starting ODS
				object_detection_system = StartODS()
				object_detection_system.start()
				# Set the incoming video from the object_detection.py on top of the label
				object_detection_system.ImageUpdate.connect(video_stream_update)
				
				# Create label to show detection stats
				show_detection_stats = create_label()
				widgets["show_detection_stats_ods"].append(show_detection_stats)
				show_detection_stats.setAlignment(QtCore.Qt.AlignJustify)
				# Set the incoming string from the object_detection.py on top of the label
				object_detection_system.odsDetectionStats.connect(detection_stats_update)
				
				# Create sto button that will call the stop_operation method
				stop_button_ods = create_button("Stop")
				stop_button_ods.clicked.connect(stop_operation)
				widgets["stop_button_ods"].append(stop_button_ods)
				
				# Return the widgets to DNDS page is the call came from DNDS page
				if return_items:
					# Set Frame size according to the window
					video_feed_ods.setFixedSize(560, 315)
					return object_detection_system
				# Show the widgets in a separate page
				else:
					# Set Frame size according to the window
					video_feed_ods.setFixedSize(800, 450)
					grid.addWidget(widgets["show_detection_stats_ods"][-1], 0, 0, 1, 4)
					grid.addWidget(widgets["video_feed_ods"][-1], 1, 0, 1, 4)
					grid.addWidget(widgets["stop_button_ods"][-1], 2, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError:
				start_operation("HOME")
		
		# Pedestrian Detection System page
		def page_pds(return_items):
			# Update the video stream constantly while receiving frames from the pedestrian_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				make_frame_rounded(video_feed_pds, frame, antialiasing=False)
			
			# Update the detection stats constantly while receiving data from the pedestrian_detection.py file
			def detection_stats_update(stats):
				show_detection_stats_pds.setText(stats)
			
			# Method to stop the object detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				start_operation("HOME")
				pedestrian_detection_system.stop()
			
			try:
				# Create a label to display video on top of it
				video_feed_pds = create_label()
				widgets["video_feed_pds"].append(video_feed_pds)
				
				# Create a thread using ODS thread class and start the thread thereby starting PDS
				pedestrian_detection_system = StartPDS()
				pedestrian_detection_system.start()
				# Set the incoming video from the pedestrian_detection.py on top of the label
				pedestrian_detection_system.ImageUpdate.connect(video_stream_update)
				
				# Create label to show detection stats
				show_detection_stats_pds = create_label()
				show_detection_stats_pds.setAlignment(QtCore.Qt.AlignJustify)
				widgets["show_detection_stats_pds"].append(show_detection_stats_pds)
				# Set the incoming string from the pedestrian_detection.py on top of the label
				pedestrian_detection_system.TotalPeople.connect(detection_stats_update)
				
				# Create sto button that will call the stop_operation method
				stop_button_pds = create_button("Stop")
				stop_button_pds.clicked.connect(stop_operation)
				widgets["stop_button_pds"].append(stop_button_pds)
				
				# Return the widgets to DNDS page is the call came from DNDS page
				if return_items:
					# Set Frame size according to the window
					video_feed_pds.setFixedSize(560, 315)
					return pedestrian_detection_system
				# Show the widgets in a separate page
				else:
					# Set Frame size according to the window
					video_feed_pds.setFixedSize(800, 450)
					grid.addWidget(widgets["show_detection_stats_pds"][-1], 0, 0, 1, 4)
					grid.addWidget(widgets["video_feed_pds"][-1], 1, 0, 1, 4)
					grid.addWidget(widgets["stop_button_pds"][-1], 2, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError or Exception:
				start_operation("HOME")
		
		# Drowsiness Dissuader System page
		def page_dnds():
			# Method to stop the object detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				start_operation("HOME")
				drowsiness_detection_system.stop()
				lane_detection_system.stop()
				object_detection_system.stop()
				pedestrian_detection_system.stop()
			
			# pedestrian_detection_system.stop()
			
			try:
				# Call Lane detection system and receive the widgets
				lane_detection_system = page_lds(return_items=True)
				# Call Drowsiness detection system and receive the widgets
				drowsiness_detection_system = page_dds(return_items=True)
				# Call Object detection system and receive the widgets
				object_detection_system = page_ods(return_items=True)
				# Call Pedestrian detection system and receive the widgets
				pedestrian_detection_system = page_pds(return_items=True)
				
				# Create stop button that will call the stop_operation method
				stop_button_dnds = create_button("Stop")
				stop_button_dnds.clicked.connect(stop_operation)
				widgets["stop_button_dnds"].append(stop_button_dnds)
				
				# place DDS widgets on the grid
				grid.addWidget(widgets["show_ear_dds"][-1], 0, 0, 1, 1)
				grid.addWidget(widgets["show_mar_dds"][-1], 0, 1, 1, 1)
				grid.addWidget(widgets["video_feed_dds"][-1], 1, 0, 1, 2)
				grid.addWidget(widgets["status_update_dds"][-1], 2, 0, 1, 2)
				
				# place LDS widgets on the grid
				grid.addWidget(widgets["show_curve_radius_lds"][-1], 0, 2, 1, 1)
				grid.addWidget(widgets["show_curve_offset_lds"][-1], 0, 3, 1, 1)
				grid.addWidget(widgets["video_feed_lds"][-1], 1, 2, 1, 2)
				grid.addWidget(widgets["status_update_lds"][-1], 2, 2, 1, 2)
				
				# place ODS widgets on the grid
				grid.addWidget(widgets["show_detection_stats_ods"][-1], 4, 0, 1, 2)
				grid.addWidget(widgets["video_feed_ods"][-1], 5, 0, 1, 2)
				
				# place PDS widgets on the grid
				grid.addWidget(widgets["show_detection_stats_pds"][-1], 4, 2, 1, 2)
				grid.addWidget(widgets["video_feed_pds"][-1], 5, 2, 1, 2)
				
				# place the stop widget on the grid
				grid.addWidget(widgets["stop_button_dnds"][-1], 6, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError or Exception:
				start_operation("HOME")
		
		# Home page of Drowsiness dissuader system
		def home_page():
			try:
				# header widget
				header = create_label()
				header.setObjectName("header")
				header.setText("Driving Negligence Dissuader")
				header.setAlignment(QtCore.Qt.AlignCenter)
				widgets["header"].append(header)
				
				# Exit Driving Negligence Dissuader System button
				close_reset_dnds = create_button("X")
				close_reset_dnds.setObjectName("close_reset_button")
				close_reset_dnds.clicked.connect(close_operation)
				close_reset_dnds.setFixedSize(25, 25)
				widgets["close_reset_dnds"].append(close_reset_dnds)
				
				# Change application stylesheet button
				theme_change = create_button("")
				theme_change.setObjectName("theme_change")
				theme_change.clicked.connect(partial(change_theme_stylesheet))
				theme_change.setFixedSize(32, 32)
				widgets["theme_change"].append(theme_change)
				
				# Start Drowsiness Detection System button
				start_dds = create_button("Drowsiness Detection")
				start_dds.clicked.connect(partial(start_operation, "DDS"))
				widgets["start_dds"].append(start_dds)
				
				# Start Yawning Detection System button
				start_lds = create_button("Lane Detection")
				start_lds.clicked.connect(partial(start_operation, "LDS"))
				widgets["start_lds"].append(start_lds)
				
				# Start Object Detection System button
				start_ods = create_button("Object Detection")
				start_ods.clicked.connect(partial(start_operation, "ODS"))
				widgets["start_ods"].append(start_ods)
				
				# Start Pedestrian Detection System button
				start_pds = create_button("Pedestrian Detection")
				start_pds.clicked.connect(partial(start_operation, "PDS"))
				widgets["start_pds"].append(start_pds)
				
				# Start Driving Negligence Dissuader System button
				start_dnds = create_button("Driving Negligence Dissuader")
				start_dnds.clicked.connect(partial(start_operation, "DNDS"))
				widgets["start_dnds"].append(start_dnds)
				
				# footer widget
				footer = create_label()
				footer.setObjectName("footer")
				footer_text = \
					'Driving Negligence Dissuader System (DNDS) is a vehicle safety system that detects drivers ' \
					'drowsiness and yawning.\nThe system also monitors the road in front to detect the road lanes ' \
					'and other object in front of the vehicle'
				footer.setAlignment(QtCore.Qt.AlignCenter)
				footer.setText(footer_text)
				footer.setWordWrap(True)
				widgets["footer"].append(footer)
				
				# place widgets on the grid
				grid.addWidget(widgets["close_reset_dnds"][-1], 0, 0, 1, 1)
				grid.addWidget(widgets["theme_change"][-1], 0, 3, 1, 1)
				grid.addWidget(widgets["header"][-1], 1, 0, 1, 4)
				grid.addWidget(widgets["start_dds"][-1], 2, 0, 1, 2)
				grid.addWidget(widgets["start_lds"][-1], 2, 2, 1, 2)
				grid.addWidget(widgets["start_ods"][-1], 3, 0, 1, 2)
				grid.addWidget(widgets["start_pds"][-1], 3, 2, 1, 2)
				grid.addWidget(widgets["start_dnds"][-1], 4, 0, 1, 4)
				grid.addWidget(widgets["footer"][-1], 5, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError or Exception:
				start_operation("HOME")
		
		# Start the home page uon launching the application
		start_operation("HOME")


# Initialize the application and create the window object in main method
if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = DNDS()
	window.show()
	sys.exit(app.exec())
