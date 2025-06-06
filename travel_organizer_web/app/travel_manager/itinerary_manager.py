import os
import json
import uuid
import shutil

# Define base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
POSTERS_DIR = os.path.join(MEDIA_DIR, 'posters')
DOCUMENTS_DIR = os.path.join(MEDIA_DIR, 'documents')

# Ensure data and media directories exist (though they should from step 1)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(POSTERS_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

def _generate_unique_filename(directory, original_filename):
    """Generates a unique filename by prefixing with a short UUID if a file with the original name already exists."""
    name, ext = os.path.splitext(original_filename)
    filename = original_filename
    counter = 1
    # To prevent excessively long names if many files have the same name,
    # we'll use a short unique prefix if the direct name is taken.
    while os.path.exists(os.path.join(directory, filename)):
        # Try a short UUID prefix to ensure uniqueness if simple counting fails or seems clumsy
        short_uuid = str(uuid.uuid4())[:8]
        filename = f"{name}_{short_uuid}{ext}"
        # As a fallback if somehow the short_uuid version also exists (highly unlikely)
        if os.path.exists(os.path.join(directory, filename)):
             filename = f"{name}_{counter}{ext}"
             counter += 1
    return filename

def add_itinerary(title: str, poster_original_path: str, simplified_text: str, word_doc_original_path: str, details_text: str, contact_info: str):
    """
    Adds a new travel itinerary to the system.

    Args:
        title: The title of the itinerary.
        poster_original_path: The filesystem path to the original poster image.
        simplified_text: A brief version of the itinerary.
        word_doc_original_path: The filesystem path to the original Word document.
        details_text: Detailed information about the itinerary.
        contact_info: Local contact information.

    Returns:
        The ID of the newly created itinerary, or None if an error occurred.
    """
    itinerary_id = str(uuid.uuid4())

    final_poster_filename = None
    if poster_original_path and os.path.exists(poster_original_path):
        original_poster_name = os.path.basename(poster_original_path)
        poster_filename = _generate_unique_filename(POSTERS_DIR, original_poster_name)
        destination_poster_path = os.path.join(POSTERS_DIR, poster_filename)
        try:
            shutil.copy2(poster_original_path, destination_poster_path)
            final_poster_filename = poster_filename
        except Exception as e:
            print(f"Error copying poster: {e}")
            # Potentially clean up if one file fails after another succeeds
            return None

    final_word_doc_filename = None
    if word_doc_original_path and os.path.exists(word_doc_original_path):
        original_doc_name = os.path.basename(word_doc_original_path)
        doc_filename = _generate_unique_filename(DOCUMENTS_DIR, original_doc_name)
        destination_doc_path = os.path.join(DOCUMENTS_DIR, doc_filename)
        try:
            shutil.copy2(word_doc_original_path, destination_doc_path)
            final_word_doc_filename = doc_filename
        except Exception as e:
            print(f"Error copying Word document: {e}")
            # Clean up already copied poster if doc copy fails
            if final_poster_filename and os.path.exists(os.path.join(POSTERS_DIR, final_poster_filename)):
                os.remove(os.path.join(POSTERS_DIR, final_poster_filename))
            return None

    itinerary_data = {
        'id': itinerary_id,
        'title': title,
        'poster_filename': final_poster_filename,
        'simplified_itinerary_text': simplified_text,
        'word_document_filename': final_word_doc_filename,
        'detailed_info_text': details_text,
        'local_contact_info': contact_info,
        # Consider adding creation/update timestamps
        # 'created_at': datetime.utcnow().isoformat(),
        # 'updated_at': datetime.utcnow().isoformat(),
    }

    json_filepath = os.path.join(DATA_DIR, f"{itinerary_id}.json")

    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(itinerary_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing JSON data: {e}")
        # Clean up copied files if JSON writing fails
        if final_poster_filename and os.path.exists(os.path.join(POSTERS_DIR, final_poster_filename)):
            os.remove(os.path.join(POSTERS_DIR, final_poster_filename))
        if final_word_doc_filename and os.path.exists(os.path.join(DOCUMENTS_DIR, final_word_doc_filename)):
            os.remove(os.path.join(DOCUMENTS_DIR, final_word_doc_filename))
        return None

    return itinerary_id

def get_itinerary(itinerary_id: str):
    """Retrieves a specific itinerary by its ID."""
    json_filepath = os.path.join(DATA_DIR, f"{itinerary_id}.json")
    if not os.path.exists(json_filepath):
        return None
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Add full paths for media files for convenience
            if data.get('poster_filename'):
                data['poster_full_path'] = os.path.join(POSTERS_DIR, data['poster_filename'])
            else:
                data['poster_full_path'] = None
            if data.get('word_document_filename'):
                data['word_document_full_path'] = os.path.join(DOCUMENTS_DIR, data['word_document_filename'])
            else:
                data['word_document_full_path'] = None
            return data
    except Exception as e:
        print(f"Error reading itinerary {itinerary_id}: {e}")
        return None

def get_all_itineraries():
    """Retrieves a list of all itineraries (summary: id, title)."""
    itineraries = []
    if not os.path.exists(DATA_DIR):
        return itineraries

    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json') and filename != 'sample_itinerary.json':
            itinerary_id = filename[:-5] # Remove .json
            data = get_itinerary(itinerary_id) # Use existing function to load full data
            if data:
                 # For summary, we might only need id and title
                 # itineraries.append({'id': data['id'], 'title': data['title']})
                 itineraries.append(data) # For now, returning full data
    return itineraries

def find_itineraries(search_term: str):
    """Finds itineraries based on a search term in title, simplified text, or details."""
    matches = []
    if not search_term: # Return all if search term is empty, or handle as error?
        return get_all_itineraries() # Or [] depending on desired behavior

    search_term_lower = search_term.lower()
    all_itineraries = get_all_itineraries() # Leverage existing function

    for itinerary in all_itineraries:
        if (search_term_lower in itinerary.get('title', '').lower() or
            search_term_lower in itinerary.get('simplified_itinerary_text', '').lower() or
            search_term_lower in itinerary.get('detailed_info_text', '').lower()):
            matches.append(itinerary)
    return matches

def update_itinerary(itinerary_id: str, update_data: dict):
    """
    Updates an existing itinerary.
    'update_data' is a dictionary where keys are itinerary fields to be updated.
    Special keys 'poster_original_path' and 'word_doc_original_path' can be used to update files.
    """
    json_filepath = os.path.join(DATA_DIR, f"{itinerary_id}.json")
    if not os.path.exists(json_filepath):
        print(f"Error: Itinerary {itinerary_id} not found.")
        return False

    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
    except Exception as e:
        print(f"Error reading itinerary {itinerary_id} for update: {e}")
        return False

    # Handle poster file update
    new_poster_original_path = update_data.pop('poster_original_path', None)
    if new_poster_original_path and os.path.exists(new_poster_original_path):
        # Remove old poster if it exists
        old_poster_filename = current_data.get('poster_filename')
        if old_poster_filename and os.path.exists(os.path.join(POSTERS_DIR, old_poster_filename)):
            os.remove(os.path.join(POSTERS_DIR, old_poster_filename))

        # Add new poster
        original_poster_name = os.path.basename(new_poster_original_path)
        poster_filename = _generate_unique_filename(POSTERS_DIR, original_poster_name)
        destination_poster_path = os.path.join(POSTERS_DIR, poster_filename)
        try:
            shutil.copy2(new_poster_original_path, destination_poster_path)
            current_data['poster_filename'] = poster_filename
        except Exception as e:
            print(f"Error updating poster: {e}")
            # Decide on rollback or partial update strategy if necessary
            # For now, we continue and the poster_filename might remain the old one or be None

    # Handle Word document update
    new_word_doc_original_path = update_data.pop('word_doc_original_path', None)
    if new_word_doc_original_path and os.path.exists(new_word_doc_original_path):
        # Remove old document
        old_doc_filename = current_data.get('word_document_filename')
        if old_doc_filename and os.path.exists(os.path.join(DOCUMENTS_DIR, old_doc_filename)):
            os.remove(os.path.join(DOCUMENTS_DIR, old_doc_filename))

        # Add new document
        original_doc_name = os.path.basename(new_word_doc_original_path)
        doc_filename = _generate_unique_filename(DOCUMENTS_DIR, original_doc_name)
        destination_doc_path = os.path.join(DOCUMENTS_DIR, doc_filename)
        try:
            shutil.copy2(new_word_doc_original_path, destination_doc_path)
            current_data['word_document_filename'] = doc_filename
        except Exception as e:
            print(f"Error updating Word document: {e}")

    # Update other textual data
    for key, value in update_data.items():
        if key in current_data: # Only update existing keys for safety, or allow new keys?
            current_data[key] = value

    # current_data['updated_at'] = datetime.utcnow().isoformat() # If using timestamps

    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing updated JSON data for {itinerary_id}: {e}")
        return False

def delete_itinerary(itinerary_id: str):
    """Deletes an itinerary and its associated files."""
    json_filepath = os.path.join(DATA_DIR, f"{itinerary_id}.json")

    if not os.path.exists(json_filepath):
        print(f"Error: Itinerary {itinerary_id} not found for deletion.")
        return False

    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading itinerary {itinerary_id} before deletion: {e}")
        return False # Or proceed to delete files if JSON is corrupt but ID is known?

    # Delete media files
    poster_filename = data.get('poster_filename')
    if poster_filename:
        poster_path = os.path.join(POSTERS_DIR, poster_filename)
        if os.path.exists(poster_path):
            try:
                os.remove(poster_path)
            except Exception as e:
                print(f"Error deleting poster file {poster_path}: {e}")
                # Decide if failure to delete a media file should halt the whole operation

    doc_filename = data.get('word_document_filename')
    if doc_filename:
        doc_path = os.path.join(DOCUMENTS_DIR, doc_filename)
        if os.path.exists(doc_path):
            try:
                os.remove(doc_path)
            except Exception as e:
                print(f"Error deleting document file {doc_path}: {e}")

    # Delete JSON data file
    try:
        os.remove(json_filepath)
        return True
    except Exception as e:
        print(f"Error deleting JSON file {json_filepath}: {e}")
        return False

# Example usage (can be removed or moved to a test script)
if __name__ == '__main__':
    print("Itinerary Manager Module")
    # A simple test:
    # Create dummy files to act as poster and doc
    if not os.path.exists("dummy_poster.jpg"): open("dummy_poster.jpg", "w").write("poster_content")
    if not os.path.exists("dummy_doc.docx"): open("dummy_doc.docx", "w").write("doc_content")

    new_id = add_itinerary(
        title="Test Trip to Beach",
        poster_original_path="dummy_poster.jpg", # Provide path to a sample image
        simplified_text="Relax and swim.",
        word_doc_original_path="dummy_doc.docx", # Provide path to a sample doc
        details_text="A wonderful beach vacation package.",
        contact_info="Hotel California, 123-456-7890"
    )

    if new_id:
        print(f"Added itinerary with ID: {new_id}")

        print("\nAll itineraries:")
        all_items = get_all_itineraries()
        for item in all_items:
            print(f"  ID: {item['id']}, Title: {item['title']}")

        print(f"\nDetails for {new_id}:")
        trip_details = get_itinerary(new_id)
        if trip_details:
            print(json.dumps(trip_details, indent=2))
            # Example of how to access full paths
            print(f"Poster full path: {trip_details.get('poster_full_path')}")
            print(f"Document full path: {trip_details.get('word_document_full_path')}")


        print("\nSearching for 'beach':")
        beach_trips = find_itineraries("beach")
        for trip in beach_trips:
            print(f"  Found: {trip['title']}")

        print(f"\nUpdating itinerary {new_id}:")
        # Create another dummy file for update
        if not os.path.exists("updated_doc.docx"): open("updated_doc.docx", "w").write("updated_content")
        update_success = update_itinerary(new_id, {
            "simplified_text": "Relax, swim, and surf!",
            "word_doc_original_path": "updated_doc.docx" # Test updating a document
        })
        if update_success:
            print("Update successful. Verifying:")
            updated_details = get_itinerary(new_id)
            print(json.dumps(updated_details, indent=2))

        # print(f"\nDeleting itinerary {new_id}:")
        # delete_success = delete_itinerary(new_id)
        # if delete_success:
        #     print(f"Itinerary {new_id} deleted successfully.")
        #     # Verify deletion
        #     print("All itineraries after deletion:")
        #     all_items_after_delete = get_all_itineraries()
        #     for item in all_items_after_delete:
        #         print(f"  ID: {item['id']}, Title: {item['title']}")
        #     if not get_itinerary(new_id):
        #         print(f"Confirmed: Itinerary {new_id} no longer exists.")
        # else:
        #     print(f"Failed to delete itinerary {new_id}.")

    else:
        print("Failed to add itinerary.")

    # Clean up dummy files
    if os.path.exists("dummy_poster.jpg"): os.remove("dummy_poster.jpg")
    if os.path.exists("dummy_doc.docx"): os.remove("dummy_doc.docx")
    if os.path.exists("updated_doc.docx"): os.remove("updated_doc.docx")
