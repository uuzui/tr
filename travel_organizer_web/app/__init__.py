from flask import Flask

# Initialize the Flask application
app_instance = Flask(__name__)

# Configuration can be added here, e.g., app_instance.config['SECRET_KEY'] = 'your_secret_key'
# For serving media files, we'll need to configure static folder for media or use send_from_directory
# The travel_manager.MEDIA_DIR will be important here.
# We'll likely need a route to serve these files securely.

# Import routes (must be after app_instance initialization)
from app import routes

# If travel_manager is inside 'app', adjust its internal paths or ensure it can find its 'data' and 'media'
# One way is to make travel_manager configurable for its data/media paths.
# For now, we assume travel_manager.py might need adjustment if its BASE_DIR logic
# (os.path.dirname(os.path.abspath(__file__))) is affected by being a sub-module.
# A quick check on travel_manager.py:
# BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # This will be app/travel_manager
# DATA_DIR = os.path.join(BASE_DIR, 'data') # This should correctly point to app/travel_manager/data
# MEDIA_DIR = os.path.join(BASE_DIR, 'media') # Correctly app/travel_manager/media
# This seems okay.
