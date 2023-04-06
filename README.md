# Step-By-Step guide on how to get the project running
Watch - https://www.youtube.com/watch?v=dTuUm56Euo0

- Open DNDS project in your code editor (PyCharm Recommended, VsCode or any other editor will work too as long as you know how to use them)

- Create a python vitual environment ```venv``` inside ```Driving_Negligence_Dissuader_System/``` like so ```Driving_Negligence_Dissuader_System/venv```

- Run the commands below to create and activate the vitual environment. (If you are using PyCharm, you can create a virtual environment in the  settings/python_interpretor section)

        python3.8 -m venv venv
        
        source venv/bin/activate


- Install all the dependencies listed in the ```requirements.txt``` file (You can install the requirements manually one by one or you can install them all by running the following command. Make sure you install the specified versions, as other versions might not work)

        pip install -r requirements.txt

- Wait for the requirements to install and the interpreter to update.

- Run ```__init__.py``` to run the project.



Note: If you want to use different video for input or you want to use video input from a camera, you can change the value of ```video_stream``` variable in each of the detection.py file.


drowsy_yawn_detection.py

<img width="896" alt="Picture 3" src="https://user-images.githubusercontent.com/51450993/226995993-40716383-ab20-45d3-9268-21c6cfd238ff.png">

lane_detection.py

<img width="896" alt="Picture 3" src="https://user-images.githubusercontent.com/51450993/227026303-41501762-9004-44fd-b279-7c3f79cff1a5.png">

object_detection.py

<img width="896" alt="Picture 3" src="https://user-images.githubusercontent.com/51450993/226996044-bc602dd6-f6c4-4969-9480-394eba6de806.png">





# Driving_Negligence_Dissuader_System
DNDS is a vehicle safety recommendation system that monitors the driver’s facial behaviour to detect the driver’s drowsiness and yawning. The system also monitors the road in front to detect the road lanes, the lane curvature, the vehicle centre offset, and objects of multiple classes on the road, such as humans, animals, and other vehicles, etc.

The homepage is where the user interacts with multiple functionalities that the system provides such as Drowsiness Detection System (DDS), Yawning Detection System (YDS), Lane Detection System (LDS), and Object Detection System (ODS), etc. There are multiple components for the user to interact with. Most notably the Drowsiness Detection, Yawning Detection, Object Detection, Pedestrian Detection. And Driving Negligence Dissuader buttons.

<img width="896" alt="Screenshot 2023-01-27 at 4 56 34 PM" src="https://user-images.githubusercontent.com/51450993/215087900-577c12c3-5ce2-4924-9467-cac29753f43c.png">

When a user decides to click the Drowsiness Detection button on the home page, they are switched to the DDS/YDS page. Here the user is facilitated with information about Eye Aspect Ratio (EAR), Mouth Aspect Ratio (MAR), and the number of detections. A live video session shows the drowsiness and yawing detections in real-time.

<img width="896" alt="Picture 1" src="https://user-images.githubusercontent.com/51450993/215087928-7a5fc4e1-c333-4780-86be-0061d1e8b2a3.png">

When a user decides to click the Lane Detection button on the home page, they are switched to the YDS page. Here, the user is facilitated with information about the Curve Radius (CR) and the Vehicle Center Offset (VCO) of the vehicle from the lane. A live video session shows the highlighted lane in real-time. The user is warned of any detections by an audio message as well as a warning message below the video footage when the system the vehicle wandering off their lane.

<img width="896" alt="Picture 2" src="https://user-images.githubusercontent.com/51450993/215087955-ef956834-0b72-404d-a766-891ca25a3b36.png">

When a user decides to click the Object Detection button on the home page, they are switched to the ODS page. Here the user is facilitated with information about the detected objects and the number of items of the same class. A real-time video session shows the objects enclosed in bounding boxes and the detection confidence for that object.

<img width="896" alt="Picture 3" src="https://user-images.githubusercontent.com/51450993/215087987-2a4d8615-a61b-4954-b0ef-27ba3da49f91.png">

When a user decides to click the Driving Negligence Dissuader button on the home page, they are switched to the DND page. Here, the user is facilitated with all the information about each detection system in their designated corner. Live video sessions for each system show the detections in real-time. The user is warned of any detections by an audio message as well as a warning message below the video footage of the system, where the warning is generated upon detection.

<img width="896" alt="Picture 3" src="https://user-images.githubusercontent.com/51450993/215088324-253945ac-f54b-4dc0-bca0-8e2a9fdd0601.png">
