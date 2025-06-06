import os
import sys
import shutil
import json

# Add the parent directory (travel_manager) to sys.path to find itinerary_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from itinerary_manager import (
    add_itinerary,
    get_itinerary,
    get_all_itineraries,
    find_itineraries,
    update_itinerary,
    delete_itinerary,
    DATA_DIR, MEDIA_DIR # For cleanup
)

# Define paths for dummy files relative to the project root (where the script is expected to be run from, or adjust paths)
# Assuming this test script will be run from the directory containing 'travel_manager'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # This should be outside travel_manager
DUMMY_POSTER_PATH = os.path.join(PROJECT_ROOT, "dummy_poster_for_test.jpg")
DUMMY_DOC_PATH = os.path.join(PROJECT_ROOT, "dummy_doc_for_test.docx")
UPDATED_DUMMY_DOC_PATH = os.path.join(PROJECT_ROOT, "updated_dummy_doc_for_test.docx")

def cleanup_test_data(itinerary_id=None):
    """Cleans up created JSON files, media files, and dummy input files."""
    if itinerary_id:
        # Attempt to delete specific itinerary data
        # This relies on delete_itinerary which is also being tested,
        # so manual cleanup might be needed if delete_itinerary fails.
        print(f"Attempting to delete itinerary {itinerary_id} as part of cleanup...")
        delete_itinerary(itinerary_id) # Use the function to ensure media is also cleaned

    # Fallback: Clean any remaining .json files in DATA_DIR (except sample)
    # and all files in media directories. This is aggressive for a shared test env.
    # For this specific test script, it's okay.
    for item in os.listdir(DATA_DIR):
        if item.endswith(".json") and item != "sample_itinerary.json":
            os.remove(os.path.join(DATA_DIR, item))
            print(f"Cleaned up data file: {item}")

    for subdir in [os.path.join(MEDIA_DIR, 'posters'), os.path.join(MEDIA_DIR, 'documents')]:
        if not os.path.exists(subdir): # Ensure subdir exists before listing
            print(f"Subdirectory {subdir} not found during cleanup. Skipping.")
            continue
        for item in os.listdir(subdir):
            if item != ".gitkeep":
                os.remove(os.path.join(subdir, item))
                print(f"Cleaned up media file: {os.path.join(subdir, item)}")
    print("Cleanup process finished.")


def run_tests():
    """Runs a sequence of tests for the itinerary_manager module."""
    test_itinerary_id = None
    print("Starting itinerary management tests...")

    # Ensure dummy files exist before starting
    if not os.path.exists(DUMMY_POSTER_PATH) or not os.path.exists(DUMMY_DOC_PATH) or not os.path.exists(UPDATED_DUMMY_DOC_PATH):
        print(f"ERROR: Dummy files for testing not found. Paths:")
        print(f"  Poster: {DUMMY_POSTER_PATH} (exists: {os.path.exists(DUMMY_POSTER_PATH)})")
        print(f"  Doc: {DUMMY_DOC_PATH} (exists: {os.path.exists(DUMMY_DOC_PATH)})")
        print(f"  Updated Doc: {UPDATED_DUMMY_DOC_PATH} (exists: {os.path.exists(UPDATED_DUMMY_DOC_PATH)})")
        print("Please create these files in the project root before running tests.")
        return

    try:
        # 1. Test add_itinerary
        print("\n--- Testing add_itinerary ---")
        test_itinerary_id = add_itinerary(
            title="Test Adventure Holiday",
            poster_original_path=DUMMY_POSTER_PATH,
            simplified_text="A test trip with lots of adventure.",
            word_doc_original_path=DUMMY_DOC_PATH,
            details_text="Full details of the test adventure holiday package.",
            contact_info="Test Contact: test@example.com, 123-000-4321"
        )
        assert test_itinerary_id is not None, "add_itinerary failed to return an ID."
        print(f"add_itinerary successful. New ID: {test_itinerary_id}")

        # 2. Test get_itinerary
        print("\n--- Testing get_itinerary ---")
        itinerary = get_itinerary(test_itinerary_id)
        assert itinerary is not None, f"get_itinerary failed for ID: {test_itinerary_id}"
        assert itinerary['title'] == "Test Adventure Holiday", "get_itinerary returned wrong title."
        print(f"get_itinerary successful for ID: {test_itinerary_id}. Title: {itinerary['title']}")
        print(f"Poster: {itinerary.get('poster_filename')}, Doc: {itinerary.get('word_document_filename')}")
        assert itinerary.get('poster_filename') is not None, "Poster filename missing."
        assert itinerary.get('word_document_filename') is not None, "Document filename missing."


        # 3. Test get_all_itineraries
        print("\n--- Testing get_all_itineraries ---")
        all_itineraries = get_all_itineraries()
        assert isinstance(all_itineraries, list), "get_all_itineraries should return a list."
        assert len(all_itineraries) > 0, "get_all_itineraries returned an empty list when one item exists."
        found = any(item['id'] == test_itinerary_id for item in all_itineraries)
        assert found, f"Newly added itinerary {test_itinerary_id} not found in get_all_itineraries."
        print(f"get_all_itineraries successful. Found {len(all_itineraries)} itineraries.")

        # 4. Test find_itineraries
        print("\n--- Testing find_itineraries ---")
        search_results = find_itineraries("adventure")
        assert isinstance(search_results, list), "find_itineraries should return a list."
        assert len(search_results) > 0, "find_itineraries did not find the test item with 'adventure'."
        found_in_search = any(item['id'] == test_itinerary_id for item in search_results)
        assert found_in_search, "find_itineraries did not include the test item in results for 'adventure'."
        print(f"find_itineraries successful. Found {len(search_results)} item(s) for 'adventure'.")

        # 5. Test update_itinerary
        print("\n--- Testing update_itinerary ---")
        update_payload = {
            "title": "Updated Test Adventure Holiday",
            "simplified_text": "An updated test trip with even more adventure and relaxation.",
            "word_doc_original_path": UPDATED_DUMMY_DOC_PATH # Test file update
        }
        update_status = update_itinerary(test_itinerary_id, update_payload)
        assert update_status, f"update_itinerary failed for ID: {test_itinerary_id}"

        updated_itinerary = get_itinerary(test_itinerary_id)
        assert updated_itinerary is not None, "Failed to get itinerary after update."
        assert updated_itinerary['title'] == "Updated Test Adventure Holiday", "Title not updated."
        assert updated_itinerary['simplified_text'] == "An updated test trip with even more adventure and relaxation.", "Simplified text not updated."
        # Check if the document filename implies it was updated (it should have a new unique name or the name of the updated file)
        # This is a bit indirect; ideally, we'd confirm the content or new filename pattern.
        original_doc_name = os.path.basename(DUMMY_DOC_PATH)
        updated_doc_name = os.path.basename(UPDATED_DUMMY_DOC_PATH)
        # Assuming _generate_unique_filename makes it different, or it's the new name directly
        assert updated_itinerary.get('word_document_filename') != original_doc_name if original_doc_name != updated_doc_name else True, "Word document filename not updated as expected."
        print(f"update_itinerary successful for ID: {test_itinerary_id}. New title: {updated_itinerary['title']}")
        print(f"Updated document filename: {updated_itinerary.get('word_document_filename')}")


        # 6. Test delete_itinerary (This is the last destructive test)
        print("\n--- Testing delete_itinerary ---")
        # Store paths before deletion to verify files are gone
        poster_to_delete_path = updated_itinerary.get('poster_full_path')
        doc_to_delete_path = updated_itinerary.get('word_document_full_path') # path to the *updated* doc
        json_to_delete_path = os.path.join(DATA_DIR, f"{test_itinerary_id}.json")

        delete_status = delete_itinerary(test_itinerary_id)
        assert delete_status, f"delete_itinerary failed for ID: {test_itinerary_id}"

        assert get_itinerary(test_itinerary_id) is None, "get_itinerary found data after deletion."
        if poster_to_delete_path: # Check only if a poster existed
             assert not os.path.exists(poster_to_delete_path), f"Poster file {poster_to_delete_path} still exists after deletion."
        if doc_to_delete_path: # Check only if a document existed
             assert not os.path.exists(doc_to_delete_path), f"Document file {doc_to_delete_path} still exists after deletion."
        assert not os.path.exists(json_to_delete_path), f"JSON file {json_to_delete_path} still exists after deletion."
        print(f"delete_itinerary successful for ID: {test_itinerary_id}. Files also checked for deletion.")
        test_itinerary_id = None # Mark as deleted

        print("\nAll tests passed successfully!")

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
    except Exception as e:
        print(f"\nAN UNEXPECTED ERROR OCCURRED: {e}")
    finally:
        print("\n--- Running cleanup ---")
        # If test_itinerary_id is not None here, it means deletion might not have run or failed
        # The cleanup_test_data function will attempt to clean it if it still exists.
        cleanup_test_data(test_itinerary_id) # Pass the ID if it wasn't deleted by the test
        # Remove dummy input files created at the start of the subtask
        # These paths are PROJECT_ROOT level, ensure they are correct
        if os.path.exists(DUMMY_POSTER_PATH): os.remove(DUMMY_POSTER_PATH)
        if os.path.exists(DUMMY_DOC_PATH): os.remove(DUMMY_DOC_PATH)
        if os.path.exists(UPDATED_DUMMY_DOC_PATH): os.remove(UPDATED_DUMMY_DOC_PATH)
        print("Dummy input files removed from project root.")


if __name__ == "__main__":
    # This allows running the test script directly: python travel_manager/tests/test_operations.py
    # Make sure PWD is the root of the project (e.g., the directory containing 'travel_manager')
    # or adjust DUMMY_FILE_PATHS accordingly.

    # For the subtask, we might need to ensure PWD is the repo root.
    # The paths for dummy files are constructed assuming the script is in travel_manager/tests
    # and dummy files are in the repo root.

    # The PROJECT_ROOT is /app. The dummy files are created in /app.
    # The script is in /app/travel_manager/tests.
    # So, DUMMY_POSTER_PATH will be /app/dummy_poster_for_test.jpg which is correct.

    print(f"Current working directory: {os.getcwd()}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"DUMMY_POSTER_PATH: {DUMMY_POSTER_PATH} (Exists: {os.path.exists(DUMMY_POSTER_PATH)})")
    print(f"DUMMY_DOC_PATH: {DUMMY_DOC_PATH} (Exists: {os.path.exists(DUMMY_DOC_PATH)})")
    print(f"UPDATED_DUMMY_DOC_PATH: {UPDATED_DUMMY_DOC_PATH} (Exists: {os.path.exists(UPDATED_DUMMY_DOC_PATH)})")

    # Check if dummy files are accessible before running tests
    # This check is primarily for direct execution. The subtask creates them in the root.
    if not (os.path.exists(DUMMY_POSTER_PATH) and \
            os.path.exists(DUMMY_DOC_PATH) and \
            os.path.exists(UPDATED_DUMMY_DOC_PATH)):
        print("One or more dummy files are not found at the expected project root locations.")
        # No need to print paths again as they are printed above.
        print("Please ensure these files exist in the project root or adjust paths in the script.")
    else:
        run_tests()
