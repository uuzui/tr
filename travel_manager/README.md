# Travel Itinerary Management System

## Purpose

This project provides a backend system for managing travel itineraries. It allows users to store, retrieve, update, delete, and search for travel packages, including associated files like posters (images) and detailed itinerary documents (Word files).

The system is designed as a Python module (`itinerary_manager.py`) that handles the core logic and data persistence. This module can be integrated into larger applications, such as a web service or a desktop GUI application.

## Directory Structure

The project uses the following directory structure within the `travel_manager` folder:

-   **`travel_manager/`**: Root directory for the module.
    -   **`itinerary_manager.py`**: The main Python module containing all logic for managing itineraries.
    -   **`data/`**: Stores the JSON metadata files for each itinerary. Each itinerary has its own JSON file, named `<itinerary_id>.json`.
        -   `sample_itinerary.json`: An example of the JSON data structure (not used by the live system).
        -   `.gitkeep`: Ensures the directory is tracked by Git.
    -   **`media/`**: Stores all media files associated with itineraries.
        -   **`posters/`**: Contains poster images (e.g., JPG, PNG).
            -   `.gitkeep`: Ensures the directory is tracked by Git.
        -   **`documents/`**: Contains detailed itinerary documents (e.g., DOCX files).
            -   `.gitkeep`: Ensures the directory is tracked by Git.
    -   **`tests/`**: Contains test scripts for the system.
        -   `test_operations.py`: A script to run various tests on the `itinerary_manager.py` module.
    -   `README.md`: This file.

## Itinerary Data Structure

Each itinerary is represented by a JSON file in the `data/` directory (e.g., `f47ac10b-58cc-4372-a567-0e02b2c3d479.json`). The structure of this JSON file is as follows:

```json
{
  "id": "string (UUID)",
  "title": "string",
  "poster_filename": "string (filename of the poster image in media/posters/)",
  "simplified_itinerary_text": "string",
  "word_document_filename": "string (filename of the Word document in media/documents/)",
  "detailed_info_text": "string",
  "local_contact_info": "string"
}
```

-   `id`: A unique identifier for the itinerary (generated using UUID v4).
-   `title`: The name or title of the travel package.
-   `poster_filename`: The filename (including extension) of the poster image. The actual file is stored in `travel_manager/media/posters/`. This can be `null` if no poster is provided.
-   `simplified_itinerary_text`: A brief description or summary of the itinerary.
-   `word_document_filename`: The filename (including extension) of the detailed Word document. The actual file is stored in `travel_manager/media/documents/`. This can be `null` if no document is provided.
-   `detailed_info_text`: More comprehensive details about the travel package.
-   `local_contact_info`: Information about local contacts, guides, or operators.

## `itinerary_manager.py` Module Overview

The `itinerary_manager.py` module provides functions to interact with the travel itinerary data.

Key functions:

-   `add_itinerary(title, poster_original_path, simplified_text, word_doc_original_path, details_text, contact_info)`: Adds a new itinerary. Copies provided poster and document files to the media storage. Returns the ID of the new itinerary.
-   `get_itinerary(itinerary_id)`: Retrieves the full data for a specific itinerary by its ID. Includes full paths to media files (`poster_full_path`, `word_document_full_path`) in the returned dictionary.
-   `get_all_itineraries()`: Returns a list of all stored itineraries (full data for each).
-   `find_itineraries(search_term)`: Searches itineraries by a keyword in the title, simplified text, or detailed information. Returns a list of matching itineraries.
-   `update_itinerary(itinerary_id, update_data)`: Updates an existing itinerary. Can also update/replace poster and document files if their new paths are provided in `update_data` under `poster_original_path` or `word_doc_original_path`.
-   `delete_itinerary(itinerary_id)`: Deletes an itinerary's JSON data file and its associated media files (poster and document).

## Running the Tests

The `travel_manager/tests/test_operations.py` script can be used to test the functionality of the `itinerary_manager.py` module.

1.  **Prerequisites**: Ensure you have Python 3 installed.
2.  **Dummy Files**: The test script relies on dummy files being present in the project's root directory (i.e., the directory *containing* the `travel_manager` folder, not inside it). These are:
    -   `dummy_poster_for_test.jpg`
    -   `dummy_doc_for_test.docx`
    -   `updated_dummy_doc_for_test.docx`
    The test script will inform you if these are missing. You can create empty files or files with minimal content for testing purposes (e.g., using `touch dummy_poster_for_test.jpg`).
3.  **Execution**:
    -   Navigate to the project root directory (the one containing the `travel_manager` directory).
    -   Run the script using the Python interpreter:
        ```bash
        python travel_manager/tests/test_operations.py
        ```
    The script will perform a series of add, get, list, find, update, and delete operations and report its progress. It also includes cleanup of test data and the dummy files it uses (though it expects the dummy files to be created by the user/setup).

This system provides a foundational backend. Future development could include a REST API built on top of this module for web applications or integration into other user interface frameworks.
