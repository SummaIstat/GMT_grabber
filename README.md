# GMT_grabber readme  

## How to execute the program on your PC by using the terminal

If you have Python 3.X already installed on your PC you just have to apply the following instruction points:

1) create a folder on your filesystem (let's say "myDir")

2) copy the content of the project directory into "myDir"

3) customize the parameters inside the config.cfg file :
        
        If you are behind a proxy simply uncomment and customize the PROXY_HOST and PROXY_PORT parameters by removing the initial # character
        
        Change the value of the path related parameters (eg. INPUT_FILE_PATH,OUTPUT_FOLDER_PATH,MAPS_FOLDER_PATH) according with the position of the files and folders on your filesystem.

4) open a terminal and go into the myDir directory

5) if in your Python configuration (or you Python virtual environment) the dependencies required by the project are not installed, type and execute the following commands:

	pip install -U wxPython
	
 	pip install pyproj
	
  	pip install opencv-python
	
 	pip install -U matplotlib
	
 	pip install pypng
	
 	pip install -U selenium
	
 	pip install webdriver_manager

7) type and execute the following command:
        python GMT_grabber.py config.cfg

## Licensing

This software is released under the European Union Public License v. 1.2
A copy of the license is included in the project folder.


## Considerations


This program is still a work in progress so be patient if it is not completely fault tolerant; in any case feel free to contact me (donato.summa@istat.it) if you have any questions or comments.
