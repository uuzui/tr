from flask import jsonify, request, send_from_directory, abort, render_template, redirect, url_for
from app import app_instance # Import the app instance
import os
import sys
import logging # For better debugging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Add app/travel_manager to Python's search path for modules
APP_DIR = os.path.dirname(os.path.abspath(__file__))
TRAVEL_MANAGER_MODULE_DIR = os.path.join(APP_DIR, 'travel_manager')

# Check if the travel_manager directory and itinerary_manager.py exist
if not os.path.isdir(TRAVEL_MANAGER_MODULE_DIR):
    logging.error(f"Directory not found: {TRAVEL_MANAGER_MODULE_DIR}")
if not os.path.isfile(os.path.join(TRAVEL_MANAGER_MODULE_DIR, 'itinerary_manager.py')):
    logging.error(f"File not found: {os.path.join(TRAVEL_MANAGER_MODULE_DIR, 'itinerary_manager.py')}")

sys.path.insert(0, TRAVEL_MANAGER_MODULE_DIR)

ITINERARY_MEDIA_DIR = None # Initialize to None

try:
    from itinerary_manager import (
        add_itinerary,
        get_itinerary,
        get_all_itineraries,
        find_itineraries,
        update_itinerary,
        delete_itinerary,
        MEDIA_DIR as ACTUAL_ITINERARY_MEDIA_DIR
    )
    ITINERARY_MEDIA_DIR = ACTUAL_ITINERARY_MEDIA_DIR
    logging.info(f"Successfully imported itinerary_manager. MEDIA_DIR set to: {ITINERARY_MEDIA_DIR}")
except ImportError as e:
    logging.critical(f"CRITICAL: Error importing itinerary_manager: {e}")
    logging.critical(f"sys.path: {sys.path}")
    logging.critical(f"Attempted to import from: {TRAVEL_MANAGER_MODULE_DIR}")
    # Define dummy functions if import fails
    def get_all_itineraries(): return [{'id':'error', 'title': 'ERROR: itinerary_manager not loaded correctly. Check logs.'}]
    def get_itinerary(id): return None
    def add_itinerary(title, poster_original_path, simplified_text, word_doc_original_path, details_text, contact_info): return None
    def update_itinerary(id, data): return False
    def delete_itinerary(id): return False
    # Fallback for ITINERARY_MEDIA_DIR if import fails
    ITINERARY_MEDIA_DIR = os.path.join(APP_DIR, 'travel_manager/media')
    logging.warning(f"Using fallback ITINERARY_MEDIA_DIR: {ITINERARY_MEDIA_DIR}")


# --- Web Page Routes (Serve HTML) ---

@app_instance.route('/')
def main_index_redirect():
    return redirect(url_for('web_index'))

@app_instance.route('/web/')
@app_instance.route('/web/index')
def web_index():
    return render_template('index.html')

@app_instance.route('/web/itinerary/<string:itinerary_id>')
def web_view_itinerary(itinerary_id):
    itinerary_data = get_itinerary(itinerary_id)
    if not itinerary_data:
        return render_template('404.html', error_message=f"Itinerary with ID {itinerary_id} not found."), 404
    return render_template('itinerary_detail.html', itinerary=itinerary_data)

@app_instance.route('/web/itineraries/add', methods=['GET'])
def web_add_itinerary_form():
    return render_template('itinerary_form.html', form_title="Add New Itinerary")

@app_instance.route('/web/itineraries/edit/<string:itinerary_id>', methods=['GET'])
def web_edit_itinerary_form(itinerary_id):
    itinerary_data = get_itinerary(itinerary_id)
    if not itinerary_data:
        return render_template('404.html', error_message=f"Itinerary with ID {itinerary_id} not found for editing."), 404
    return render_template('itinerary_form.html', form_title=f"Edit: {itinerary_data.get('title', 'Itinerary')}", itinerary=itinerary_data)


# --- API Endpoints (Return JSON) ---

@app_instance.route('/api/itineraries', methods=['GET'])
def api_get_all_itineraries():
    all_itins = get_all_itineraries()
    return jsonify(all_itins)

@app_instance.route('/api/itineraries/<string:itinerary_id>', methods=['GET'])
def api_get_itinerary(itinerary_id):
    itinerary = get_itinerary(itinerary_id)
    if itinerary:
        return jsonify(itinerary)
    else:
        return jsonify({'error': 'Itinerary not found'}), 404

@app_instance.route('/api/itineraries', methods=['POST'])
def api_add_itinerary():
    title = request.form.get('title')
    simplified_text = request.form.get('simplified_itinerary_text')
    details_text = request.form.get('detailed_info_text')
    contact_info = request.form.get('local_contact_info')

    if not title: return jsonify({'error': 'Missing title'}), 400

    poster_file = request.files.get('poster_file')
    doc_file = request.files.get('word_document_file')

    temp_poster_path = None
    temp_doc_path = None

    # Ensure ITINERARY_MEDIA_DIR is valid before creating temp_dir
    if not ITINERARY_MEDIA_DIR or not os.path.isdir(ITINERARY_MEDIA_DIR):
        logging.error(f"ITINERARY_MEDIA_DIR ('{ITINERARY_MEDIA_DIR}') is not a valid directory. Cannot save temporary files for upload.")
        return jsonify({'error': 'Server configuration error for media path.'}), 500

    temp_dir = os.path.join(ITINERARY_MEDIA_DIR, 'temp_uploads')
    try:
        os.makedirs(temp_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Could not create temp_dir '{temp_dir}': {e}")
        return jsonify({'error': 'Server error creating temporary directory.'}), 500


    if poster_file and poster_file.filename:
        temp_poster_path = os.path.join(temp_dir, poster_file.filename) # Consider werkzeug.utils.secure_filename
        poster_file.save(temp_poster_path)

    if doc_file and doc_file.filename:
        temp_doc_path = os.path.join(temp_dir, doc_file.filename) # Consider werkzeug.utils.secure_filename
        doc_file.save(temp_doc_path)

    new_id = add_itinerary(
        title=title,
        poster_original_path=temp_poster_path,
        simplified_text=simplified_text,
        word_doc_original_path=temp_doc_path,
        details_text=details_text,
        contact_info=contact_info
    )

    if temp_poster_path and os.path.exists(temp_poster_path): os.remove(temp_poster_path)
    if temp_doc_path and os.path.exists(temp_doc_path): os.remove(temp_doc_path)

    if new_id:
        return jsonify(get_itinerary(new_id)), 201
    else:
        return jsonify({'error': 'Failed to add itinerary. Check server logs.'}), 500

@app_instance.route('/api/itineraries/<string:itinerary_id>', methods=['PUT'])
def api_update_itinerary(itinerary_id_from_url): # Renamed to avoid clash if 'itinerary_id' in form
    if not get_itinerary(itinerary_id_from_url): return jsonify({'error': 'Itinerary not found for update'}), 404

    update_data = {k:v for k,v in request.form.items()}

    temp_poster_path, temp_doc_path = None, None
    if not ITINERARY_MEDIA_DIR or not os.path.isdir(ITINERARY_MEDIA_DIR):
        logging.error(f"ITINERARY_MEDIA_DIR ('{ITINERARY_MEDIA_DIR}') is not valid for PUT. Cannot save temporary files.")
        return jsonify({'error': 'Server configuration error for media path.'}), 500
    temp_dir = os.path.join(ITINERARY_MEDIA_DIR, 'temp_uploads')
    try:
        os.makedirs(temp_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Could not create temp_dir '{temp_dir}' for PUT: {e}")
        return jsonify({'error': 'Server error creating temporary directory.'}), 500

    if 'poster_file' in request.files:
        poster_file = request.files['poster_file']
        if poster_file and poster_file.filename:
            temp_poster_path = os.path.join(temp_dir, poster_file.filename)
            poster_file.save(temp_poster_path)
            update_data['poster_original_path'] = temp_poster_path # This key is used by itinerary_manager.update_itinerary

    if 'word_document_file' in request.files:
        doc_file = request.files['word_document_file']
        if doc_file and doc_file.filename:
            temp_doc_path = os.path.join(temp_dir, doc_file.filename)
            doc_file.save(temp_doc_path)
            update_data['word_doc_original_path'] = temp_doc_path # This key is used by itinerary_manager.update_itinerary

    success = update_itinerary(itinerary_id_from_url, update_data)

    if temp_poster_path and os.path.exists(temp_poster_path): os.remove(temp_poster_path)
    if temp_doc_path and os.path.exists(temp_doc_path): os.remove(temp_doc_path)

    if success:
        return jsonify(get_itinerary(itinerary_id_from_url))
    else:
        return jsonify({'error': 'Failed to update itinerary. Check server logs.'}), 500

@app_instance.route('/api/itineraries/<string:itinerary_id>', methods=['DELETE'])
def api_delete_itinerary(itinerary_id):
    if not get_itinerary(itinerary_id): return jsonify({'error': 'Itinerary not found'}), 404
    success = delete_itinerary(itinerary_id)
    if success:
        return jsonify({'message': 'Itinerary deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete itinerary. Check server logs.'}), 500

# --- Media Serving Endpoint ---
@app_instance.route('/media/<path:type>/<path:filename>')
def serve_media(type, filename):
    if not ITINERARY_MEDIA_DIR:
        logging.error("ITINERARY_MEDIA_DIR is not set. Cannot serve media.")
        abort(500) # Internal server error

    directory_to_serve_from = os.path.join(ITINERARY_MEDIA_DIR, type)

    # Security checks
    if type not in ['posters', 'documents']:
        logging.warning(f"Invalid media type requested: {type}")
        abort(404)

    # Normalize paths to prevent traversal
    safe_directory_to_serve_from = os.path.normpath(directory_to_serve_from)
    safe_filepath = os.path.normpath(os.path.join(safe_directory_to_serve_from, filename))

    if not safe_filepath.startswith(safe_directory_to_serve_from + os.sep) and not safe_filepath == safe_directory_to_serve_from : # os.sep for paths like /media/posters/ (no filename)
         logging.warning(f"Path traversal attempt detected: {filename} from {directory_to_serve_from}")
         abort(403)

    if not os.path.exists(safe_filepath) or not os.path.isfile(safe_filepath):
        logging.info(f"Media file not found: {safe_filepath}")
        abort(404)

    logging.debug(f"Serving media file: {safe_filepath}")
    return send_from_directory(safe_directory_to_serve_from, filename)

if ITINERARY_MEDIA_DIR:
    logging.info(f"Flask App: Media serving configured for ITINERARY_MEDIA_DIR: {ITINERARY_MEDIA_DIR}")
else:
    logging.error("Flask App: ITINERARY_MEDIA_DIR is not set after imports. Media serving will likely fail.")
