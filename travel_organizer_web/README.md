# Travel Organizer Web Application

This web application provides a graphical user interface (GUI) for the Travel Itinerary Management system. It allows users to easily view, add, edit, and delete travel itineraries, including their associated posters and documents, all through a web browser.

**This application is designed to run locally and offline.**

## Features

-   **Browse Itineraries**: View all travel itineraries in a list format with thumbnails.
-   **View Details**: See detailed information for each itinerary, including poster image and a link to the detailed document.
-   **Add New Itineraries**: Upload new travel packages with title, descriptions, poster image, and a Word document.
-   **Edit Existing Itineraries**: Modify the details and files of previously added itineraries.
-   **Delete Itineraries**: Remove itineraries from the system.
-   **Modern, Responsive Interface**: The GUI is designed to be user-friendly and adaptable to different screen sizes.

## Prerequisites

-   **Python 3**: Ensure Python 3.6 or newer is installed on your system. You can download it from [python.org](https://www.python.org/).
-   **Web Browser**: A modern web browser (e.g., Chrome, Firefox, Edge, Safari).

## Setup and Installation

1.  **Navigate to Project Directory**:
    Open your terminal or command prompt and navigate to this `travel_organizer_web` directory.

2.  **Create a Virtual Environment (Recommended)**:
    It's highly recommended to use a virtual environment to manage dependencies for this project.
    ```bash
    python3 -m venv venv
    ```
    Activate the virtual environment:
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies**:
    Install the necessary Python packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    This will install Flask and any other required libraries.

## Running the Application

1.  **Start the Local Web Server**:
    Once the setup is complete and you are in the `travel_organizer_web` directory (with the virtual environment activated, if you created one), run the following command:
    ```bash
    python run.py
    ```
    You should see output indicating that the Flask development server is running, typically on `http://127.0.0.1:5000/`.

2.  **Access in Browser**:
    Open your web browser and go to the address:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

    You should now see the Travel Organizer web application interface.

## Project Structure Overview

-   **`run.py`**: The main script to start the Flask application.
-   **`requirements.txt`**: Lists Python dependencies.
-   **`app/`**: Contains the core Flask application.
    -   **`__init__.py`**: Initializes the Flask app.
    *   **`routes.py`**: Defines web page routes and API endpoints.
    -   **`static/`**: Contains static assets:
        -   `css/style.css`: Main stylesheet.
        -   `js/main.js`: Core JavaScript for frontend interactivity.
        -   `images/`: For any static images used by the GUI itself.
    -   **`templates/`**: Contains HTML templates used for rendering pages.
    -   **`travel_manager/`**: The backend module for itinerary data logic (copied from the previous project).
        -   `itinerary_manager.py`: Handles CRUD operations for itineraries.
        -   `data/`: Stores itinerary JSON metadata.
        -   `media/`: Stores itinerary posters and documents.
            - `temp_uploads/`: Temporary storage for file uploads (should be cleaned automatically).

## Notes on Offline Use

-   All necessary files (HTML, CSS, JavaScript, Python backend) are included in this project directory.
-   The application runs a local web server on your computer, so no internet connection is required after the initial setup (Python and dependency installation).
-   Data is stored locally in the `app/travel_manager/data` and `app/travel_manager/media` folders.

---
This README provides guidance for setting up and running the Travel Organizer web application.
