# PREP DEPENDENCIES
from drowsy_yawn_detection import *  # Drowsiness detection system
from object_detection import *  # Object Detection System
from functools import partial  # To send args with connect command
from lane_detection import *  # Lane Detection System
from pedestrian_detection import *
# PyQt5 items for our GUI application
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui
# Misc Dependencies
import sys  # For system functions

# Dictionary to store all the widgets of the GUI application
widgets = {
	"header": [],
	"footer": [],
	"start_dds": [],
	"start_lds": [],
	"start_ods": [],
	"start_pds": [],
	"start_dnds": [],
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


# Driving Negligence Dissuader System main class
class DNDS(QWidget):
	def __init__(self, *args, **kwargs):
		super(DNDS, self).__init__(*args, **kwargs)
		
		self.old_position = None
		# Set and style the layout of the application window
		palette = QtGui.QPalette()
		# Gradient for window background
		gradient = QLinearGradient(100, 100, 800, 800)
		gradient.setColorAt(0.0, QColor(12, 12, 12, 250))
		gradient.setColorAt(1.0, QColor(15, 15, 15, 250))
		
		palette.setBrush(QPalette.Window, QBrush(gradient))
		app.setPalette(palette)
		grid = QGridLayout()
		grid.setSpacing(10)
		self.setPalette(palette)
		self.setLayout(grid)
		self.setGeometry(0, 0, 850, 650)
		self.setFont(QFont("Nunito"))
		
		# Call clear widgets method and switch to the called page
		def start_operation(operation_id):
			clear_widgets()
			
			if operation_id == "DDS":
				page_dds(return_items=False)
				self.setFixedSize(850, 650)
			if operation_id == "LDS":
				page_lds(return_items=False)
				self.setFixedSize(850, 650)
			if operation_id == "ODS":
				page_ods(return_items=False)
				self.setFixedSize(850, 650)
			if operation_id == "PDS":
				page_pds(return_items=False)
				self.setFixedSize(850, 650)
			if operation_id == "DNDS":
				page_dnds()
				# self.centralwidget.resize(1100, 850)
				self.setFixedSize(1100, 850)
		
		# Methods to clear all the widgets in current page when switching to another page
		def clear_widgets():
			for widget in widgets:
				if widgets[widget]:
					widgets[widget][-1].hide()
				for i in range(0, len(widgets[widget])):
					widgets[widget].pop()
		
		# Method to create button with pre-set stylesheet
		def create_button(button_text):
			# Create button
			button = QPushButton(button_text)
			# Change cursor to Pointing hand upon hover
			button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
			# Creating shadow object
			shadow = QGraphicsDropShadowEffect()
			# setting blur radius (optional step)
			shadow.setBlurRadius(75)
			shadow.setColor(QColor(125, 25, 25))
			shadow.setOffset(-2.5, 2.5)
			button.setGraphicsEffect(shadow)
			# CSS styling of the button
			button.setStyleSheet("""
			*{
				color: #EEEEEE;
				font-size: 20px;
				border:1.5px solid #AE082A;
				border-radius : 30%;
				width: 50px;
				height: 50px;
				padding: 5%;
				margin: 15%;}
				
			*:hover{
			background: #AE082A;}""")
			# Return the button
			return button
		
		# Method to create labels with pre-set stylesheet
		def create_label():
			# Create label
			label = QLabel()
			label.setAlignment(QtCore.Qt.AlignCenter)
			# CSS styling of the button
			label.setStyleSheet("""
				*{
					color: #EEEEEE;
					font-size: 20px;
					border-radius: 30%;}
				*:hover{
				}""")
			# Return the label
			return label
		
		# Drowsiness Detection System page
		def page_dds(return_items):
			# Update the video stream constantly while receiving frames from the drowsy_yawn_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				video_feed_dds.setPixmap(QPixmap.fromImage(frame))
			
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
				dds_video_feed.stop()
				home_page()
			
			# Create a label to display video on top of it
			video_feed_dds = create_label()
			widgets["video_feed_dds"].append(video_feed_dds)
			
			# Create a thread using DDS thread class and start the thread thereby starting DDS
			dds_video_feed = StartDDS()
			dds_video_feed.start()
			# Set the incoming video from the drowsy_yawn_detection.py on top of the label
			dds_video_feed.ImageUpdate.connect(video_stream_update)
			
			# Create label to show EAR and Drowsy Count
			show_ear = create_label()
			widgets["show_ear_dds"].append(show_ear)
			# Set the incoming string from the drowsy_yawn_detection.py on top of the label
			dds_video_feed.DrowsyStats.connect(ear_update)
			
			# Create label to show MAR and Yawn Count
			show_mar = create_label()
			widgets["show_mar_dds"].append(show_mar)
			# Set the incoming string from the drowsy_yawn_detection.py on top of the label
			dds_video_feed.YawnStats.connect(mar_update)
			
			# Create label to show drowsy or yawning status
			status_update_dds = create_label()
			widgets["status_update_dds"].append(status_update_dds)
			# Set the incoming string from the drowsy_yawn_detection.py on top of the label
			dds_video_feed.Status.connect(status_update)
			
			# Create stop button that will call the stop_operation method
			stop_button_dds = create_button("Stop")
			stop_button_dds.clicked.connect(stop_operation)
			widgets["stop_button_dds"].append(stop_button_dds)
			
			# Return the widgets to DNDS page is the call came from DNDS page
			if return_items:
				return dds_video_feed, video_feed_dds, show_ear, show_mar, status_update_dds, stop_button_dds
			# Display the widgets in separate page
			else:
				# place widgets on the grid
				grid.addWidget(show_ear, 0, 0, 1, 2)
				grid.addWidget(show_mar, 0, 2, 1, 2)
				grid.addWidget(video_feed_dds, 1, 0, 1, 4)
				grid.addWidget(status_update_dds, 2, 0, 1, 4)
				grid.addWidget(stop_button_dds, 3, 0, 1, 4)
		
		# Lane Detection System page
		def page_lds(return_items):
			# Update the video stream constantly while receiving frames from the lane_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				video_feed_lds.setPixmap(QPixmap.fromImage(frame))
			
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
				lds_video_feed.stop()
				home_page()
			
			try:
				# Create a label to display video on top of it
				video_feed_lds = create_label()
				widgets["video_feed_lds"].append(video_feed_lds)
				
				# Create a thread using LDS thread class and start the thread thereby starting LDS
				lds_video_feed = StartLDS()
				lds_video_feed.start()
				# Set the incoming video from the lane_detection.py on top of the label
				lds_video_feed.ImageUpdate.connect(video_stream_update)
				
				# Create label to show curve radius
				show_curve_radius = create_label()
				widgets["show_curve_radius_lds"].append(show_curve_radius)
				# Set the incoming string from the lane_detection.py on top of the label
				lds_video_feed.CurveRadius.connect(curve_radius_update)
				
				# Create label to show curve offset
				show_curve_offset = create_label()
				widgets["show_curve_offset_lds"].append(show_curve_offset)
				# Set the incoming string from the lane_detection.py on top of the label
				lds_video_feed.CurveOffset.connect(curve_offset_update)
				
				# Create label to show lane status
				status_update_lds = create_label()
				widgets["status_update_lds"].append(status_update_lds)
				# Set the incoming string from the lane_detection.py on top of the label
				lds_video_feed.Status.connect(status_update)
				
				# Create stop button that will call the stop_operation method
				stop_button_lds = create_button("Stop")
				stop_button_lds.clicked.connect(stop_operation)
				widgets["stop_button_lds"].append(stop_button_lds)
				
				# Return the widgets to DNDS page is the call came from DNDS page
				if return_items:
					return lds_video_feed, video_feed_lds, show_curve_radius, show_curve_offset, status_update_lds, stop_button_lds
				# Show the widgets in a separate page
				else:
					grid.addWidget(show_curve_radius, 0, 0, 1, 2)
					grid.addWidget(show_curve_offset, 0, 2, 1, 2)
					grid.addWidget(video_feed_lds, 1, 0, 1, 4)
					grid.addWidget(status_update_lds, 2, 0, 1, 4)
					grid.addWidget(stop_button_lds, 3, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError:
				pass
		
		# Object Detection System page
		def page_ods(return_items):
			# Update the video stream constantly while receiving frames from the object_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				video_feed_ods.setPixmap(QPixmap.fromImage(frame))
			
			# Update the detection stats constantly while receiving data from the object_detection.py file
			def detection_stats_update(stats):
				show_detection_stats.setText(stats)
			
			# Method to stop the object detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				ods_video_feed.stop()
				home_page()
			
			try:
				# Create a label to display video on top of it
				video_feed_ods = create_label()
				widgets["video_feed_ods"].append(video_feed_ods)
				
				# Create a thread using ODS thread class and start the thread thereby starting ODS
				ods_video_feed = StartODS()
				ods_video_feed.start()
				# Set the incoming video from the object_detection.py on top of the label
				ods_video_feed.ImageUpdate.connect(video_stream_update)
				
				# Create label to show detection stats
				show_detection_stats = create_label()
				widgets["show_detection_stats_ods"].append(show_detection_stats)
				show_detection_stats.setAlignment(QtCore.Qt.AlignJustify)
				# Set the incoming string from the object_detection.py on top of the label
				ods_video_feed.odsDetectionStats.connect(detection_stats_update)
				
				# Create sto button that will call the stop_operation method
				stop_button_ods = create_button("Stop")
				stop_button_ods.clicked.connect(stop_operation)
				widgets["stop_button_ods"].append(stop_button_ods)
				
				# Return the widgets to DNDS page is the call came from DNDS page
				if return_items:
					return ods_video_feed, video_feed_ods, show_detection_stats, stop_button_ods
				# Show the widgets in a separate page
				else:
					grid.addWidget(show_detection_stats, 0, 0, 1, 4)
					grid.addWidget(video_feed_ods, 1, 0, 1, 4)
					grid.addWidget(stop_button_ods, 2, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError:
				pass
		
		# Pedestrian Detection System page
		def page_pds(return_items):
			# Update the video stream constantly while receiving frames from the pedestrian_detection.py file
			def video_stream_update(frame):
				# Set the frame onto th videoFeed label
				video_feed_pds.setPixmap(QPixmap.fromImage(frame))
			
			# Update the detection stats constantly while receiving data from the pedestrian_detection.py file
			def detection_stats_update(stats):
				show_detection_stats_pds.setText(stats)
			
			# Method to stop the object detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				pds_video_feed.stop()
				home_page()
			
			try:
				# Create a label to display video on top of it
				video_feed_pds = create_label()
				widgets["video_feed_pds"].append(video_feed_pds)
				
				# Create a thread using ODS thread class and start the thread thereby starting PDS
				pds_video_feed = StartPDS()
				pds_video_feed.start()
				# Set the incoming video from the pedestrian_detection.py on top of the label
				pds_video_feed.ImageUpdate.connect(video_stream_update)
				
				# Create label to show detection stats
				show_detection_stats_pds = create_label()
				show_detection_stats_pds.setAlignment(QtCore.Qt.AlignJustify)
				widgets["show_detection_stats_pds"].append(show_detection_stats_pds)
				# Set the incoming string from the pedestrian_detection.py on top of the label
				pds_video_feed.TotalPeople.connect(detection_stats_update)
				
				# Create sto button that will call the stop_operation method
				stop_button_pds = create_button("Stop")
				stop_button_pds.clicked.connect(stop_operation)
				widgets["stop_button_pds"].append(stop_button_pds)
				
				# Return the widgets to DNDS page is the call came from DNDS page
				if return_items:
					return pds_video_feed, video_feed_pds, show_detection_stats_pds, stop_button_pds
				# Show the widgets in a separate page
				else:
					grid.addWidget(show_detection_stats_pds, 0, 0, 1, 4)
					grid.addWidget(video_feed_pds, 1, 0, 1, 4)
					grid.addWidget(stop_button_pds, 2, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError:
				pass
		
		# Drowsiness Dissuader System page
		def page_dnds():
			# Method to stop the object detection operation and go back to home page
			def stop_operation():
				clear_widgets()
				dds_video_feed.stop()
				lds_video_feed.stop()
				ods_video_feed.stop()
				# pds_video_feed.stop()
				
				home_page()
			
			try:
				# Call Lane detection system and receive the widgets
				lds_video_feed, video_feed_lds, show_curve_radius, show_curve_offset, status_update_lds, stop_button_lds = page_lds(
					return_items=True)
				# Call Drowsiness detection system and receive the widgets
				dds_video_feed, video_feed_dds, show_ear, show_mar, status_update_dds, stop_button_dds = page_dds(
					return_items=True)
				# Call Object detection system and receive the widgets
				ods_video_feed, video_feed_ods, show_detection_stats, stop_button_ods = page_ods(return_items=True)
				# Call Pedestrian detection system and receive the widgets
				# pds_video_feed, video_feed_pds, show_detection_stats_pds, stop_button_pds = page_pds(return_items=True)
				
				# Create stop button that will call the stop_operation method
				stop_button_dnds = create_button("Stop")
				stop_button_dnds.clicked.connect(stop_operation)
				widgets["stop_button_dnds"].append(stop_button_dnds)
				
				# place DDS widgets on the grid
				grid.addWidget(show_ear, 0, 0, 1, 1)
				grid.addWidget(show_mar, 0, 1, 1, 1)
				grid.addWidget(video_feed_dds, 1, 0, 1, 2)
				grid.addWidget(status_update_dds, 2, 0, 1, 2)
				
				# place LDS widgets on the grid
				grid.addWidget(show_curve_radius, 0, 2, 1, 1)
				grid.addWidget(show_curve_offset, 0, 3, 1, 1)
				grid.addWidget(video_feed_lds, 1, 2, 1, 2)
				grid.addWidget(status_update_lds, 2, 2, 1, 2)
				
				# place ODS widgets on the grid
				grid.addWidget(show_detection_stats, 4, 0, 1, 2)
				grid.addWidget(video_feed_ods, 5, 0, 1, 2)
				
				# # place PDS widgets on the grid
				# grid.addWidget(show_detection_stats_pds, 4, 2, 1, 2)
				# grid.addWidget(video_feed_pds, 5, 2, 1, 2)
				#
				# place the stop widget on the grid
				grid.addWidget(stop_button_dnds, 6, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError:
				pass
		
		# Home page of Drowsiness dissuader system
		def home_page():
			self.setFixedSize(850, 650)
			# header widget
			header = create_label()
			header.setText("Driving Negligence Dissuader")
			header.setAlignment(QtCore.Qt.AlignCenter)
			# CSS styling of the button
			header.setStyleSheet("""*{
					color: #EEEEEE;
					font-weight: bold;
					font-size: 48px;
					padding: 35%}""")
			widgets["header"].append(header)
			try:
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
				footer_text = \
					'Driving Negligence Dissuader System (DNDS) is a vehicle safety system to detect drivers ' \
					'drowsiness and yawning. The system also monitors the road in front to detect the road lanes ' \
					'and other object in front of the vehicle'
				footer.setAlignment(QtCore.Qt.AlignCenter)
				footer.setText(footer_text)
				footer.setWordWrap(True)
				
				footer.setStyleSheet("""*{
							color: #EEEEEE;
							font-size: 14px;
							padding: 50%}""")
				widgets["footer"].append(footer)
				
				# place widgets on the grid
				grid.addWidget(widgets["header"][-1], 0, 0, 1, 4)
				grid.addWidget(widgets["start_dds"][-1], 1, 0, 1, 2)
				grid.addWidget(widgets["start_lds"][-1], 1, 2, 1, 2)
				grid.addWidget(widgets["start_ods"][-1], 2, 0, 1, 2)
				grid.addWidget(widgets["start_pds"][-1], 2, 2, 1, 2)
				grid.addWidget(widgets["start_dnds"][-1], 3, 0, 1, 4)
				grid.addWidget(widgets["footer"][-1], 4, 0, 1, 4)
			
			except TypeError or ValueError or AttributeError:
				pass
		
		# Start the home page uon launching the application
		home_page()


# Initialize the application and create the window object in main method
if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = DNDS()
	window.show()
	sys.exit(app.exec())
