#!/bin/bash

# activate virtual environment
source ../env/bin/activate

# start Django development server
python manage.py runserver 5000 &

# wait for server to start up
sleep 5

# open page in default web browser
open http://localhost:5000/

#Instructions
#Go to the "Permissions" tab and check the "Allow executing file as program" checkbox.
#Close the dialog box.
#Right-click on the shell script file and select "Open With Other Application".
#Choose a terminal emulator, such as GNOME Terminal or Konsole, and check the "Set selected application as default" checkbox.
#Click "OK" to open the script in the terminal emulator.