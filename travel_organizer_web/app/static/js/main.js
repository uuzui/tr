document.addEventListener('DOMContentLoaded', function() {
    console.log('Travel Organizer JS: Enhancing Styling, Interactivity, and Animations.');

    const itineraryListContainer = document.getElementById('itinerary-list-container');
    const itineraryForm = document.getElementById('itinerary-form');
    const formMessageContainer = document.getElementById('form-message');
    const posterFileInput = document.getElementById('poster_file');
    const imagePreviewContainer = document.createElement('div'); // Create a container for the preview
    imagePreviewContainer.className = 'image-preview-container';
    if (posterFileInput && posterFileInput.parentNode) {
         posterFileInput.parentNode.insertBefore(imagePreviewContainer, posterFileInput.nextSibling);
    }

    // Loading indicator element (optional, can be added to HTML)
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loader';
    // Example: Prepend to main container or specific sections when loading
    // if (itineraryListContainer) itineraryListContainer.parentNode.insertBefore(loadingIndicator, itineraryListContainer);


    // --- Helper function to display messages ---
    function showMessage(element, message, type = 'success') {
        if (element) {
            element.innerHTML = message; // Use innerHTML to allow simple HTML like <br>
            element.className = type;
            element.style.display = 'block';
            // Auto-hide after 5 seconds, unless it's an error that needs attention
            if (type === 'success') {
                setTimeout(() => { element.style.display = 'none'; }, 5000);
            }
        }
    }

    function showLoading(show = true) {
        // This is a placeholder. A more robust solution would involve a dedicated loading element.
        // For now, we can disable buttons or show a simple text.
        const submitButton = itineraryForm ? itineraryForm.querySelector('button[type="submit"]') : null;
        if (submitButton) submitButton.disabled = show;
        loadingIndicator.style.display = show ? 'block' : 'none';
        if(show && itineraryListContainer && itineraryListContainer.innerHTML.trim() === '') { // Show loader in list area if empty
            itineraryListContainer.innerHTML = ''; // Clear previous content
            itineraryListContainer.appendChild(loadingIndicator);
        } else if (!show && itineraryListContainer && itineraryListContainer.contains(loadingIndicator)) {
            itineraryListContainer.removeChild(loadingIndicator);
        }
    }

    // --- Image Preview for Poster ---
    if (posterFileInput) {
        posterFileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            imagePreviewContainer.innerHTML = ''; // Clear previous preview
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.alt = 'Image preview';
                    img.className = 'image-preview';
                    imagePreviewContainer.appendChild(img);
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // --- Load Itineraries on Index Page ---
    if (itineraryListContainer && (window.location.pathname.endsWith('/web/') || window.location.pathname.endsWith('/web/index'))) {
        fetchItineraries();
    }

    async function fetchItineraries() {
        showLoading(true);
        try {
            const response = await fetch('/api/itineraries');
            if (!response.ok) throw new Error(`HTTP error! status: \${response.status}`);
            const itineraries = await response.json();
            displayItineraries(itineraries);
        } catch (error) {
            console.error('Error fetching itineraries:', error);
            if (itineraryListContainer) {
                itineraryListContainer.innerHTML = '<p class="error" style="text-align:center; padding: 20px;">Failed to load itineraries. Please try refreshing.</p>';
            }
        } finally {
            showLoading(false);
        }
    }

    function displayItineraries(itineraries) {
        if (!itineraryListContainer) return;
        itineraryListContainer.innerHTML = '';

        if (itineraries.length === 0 || (itineraries.length === 1 && itineraries[0].id === 'error')) {
            let msg = '<p style="text-align:center; padding: 20px;">No itineraries found. Be the first to add one!</p>';
            if (itineraries.length === 1 && itineraries[0].id === 'error') {
                 msg = `<p class="error" style="text-align:center; padding: 20px;">\${itineraries[0].title}</p>`;
            }
            itineraryListContainer.innerHTML = msg;
            return;
        }

        itineraries.forEach(itinerary => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'itinerary-item';

            let thumbnailHTML = '';
            if (itinerary.poster_filename) {
                thumbnailHTML = `<img src="/media/posters/\${itinerary.poster_filename}" alt="\${itinerary.title} thumbnail" class="thumbnail">`;
            } else {
                thumbnailHTML = `<div class="thumbnail placeholder-thumbnail" style="width:150px; height:150px; background-color:#eee; display:flex; align-items:center; justify-content:center; color:#aaa; font-size:0.8em; text-align:center;">No Image</div>`;
            }

            // Sanitize text before inserting (basic example, consider a library for robust sanitization if user input can contain HTML)
            const simplifiedText = itinerary.simplified_itinerary_text ?
                itinerary.simplified_itinerary_text.replace(/</g, "&lt;").replace(/>/g, "&gt;").substring(0, 120) + '...' :
                'No simplified text available.';

            itemDiv.innerHTML = `
                \${thumbnailHTML}
                <div class="item-content">
                    <h3>\${itinerary.title.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</h3>
                    <p>\${simplifiedText}</p>
                    <div class="actions">
                        <a href="/web/itinerary/\${itinerary.id}" class="view-details button">View Details</a>
                        <button class="delete-button button-danger" data-id="\${itinerary.id}">Delete</button>
                    </div>
                </div>
            `;
            itineraryListContainer.appendChild(itemDiv);
        });

        document.querySelectorAll('.delete-button').forEach(button => {
            button.addEventListener('click', handleDeleteItinerary);
        });
    }

    // --- Handle Itinerary Form Submission (Add/Edit) ---
    if (itineraryForm) {
        itineraryForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            if (!validateForm()) return; // Client-side validation

            showLoading(true);
            const submitButton = itineraryForm.querySelector('button[type="submit"]');
            if (submitButton) submitButton.textContent = 'Saving...';


            const formData = new FormData(itineraryForm);
            const itineraryId = formData.get('itinerary_id');

            let url = '/api/itineraries';
            let method = 'POST';

            if (itineraryId) {
                url += `/\${itineraryId}`;
                method = 'PUT';
            }

            if (formData.get('poster_file') && formData.get('poster_file').size === 0) { // Check size for empty file
                formData.delete('poster_file');
            }
            if (formData.get('word_document_file') && formData.get('word_document_file').size === 0) { // Check size
                formData.delete('word_document_file');
            }

            try {
                const response = await fetch(url, { method: method, body: formData });
                const result = await response.json();

                if (response.ok) {
                    showMessage(formMessageContainer, `Itinerary \${itineraryId ? 'updated' : 'added'} successfully! Redirecting...`, 'success');
                    setTimeout(() => {
                        window.location.href = result.id ? `/web/itinerary/\${result.id}` : '/web/index';
                    }, 1500);
                } else {
                    showMessage(formMessageContainer, `Error: \${result.error || 'Unknown server error'}`, 'error');
                }
            } catch (error) {
                console.error('Error submitting form:', error);
                showMessage(formMessageContainer, 'An unexpected network error occurred.', 'error');
            } finally {
                showLoading(false);
                if (submitButton) submitButton.textContent = 'Save Itinerary';
            }
        });
    }

    function validateForm() {
        let isValid = true;
        const title = document.getElementById('title');
        const simplifiedText = document.getElementById('simplified_itinerary_text');

        if (!title.value.trim()) {
            showMessage(formMessageContainer, 'Title is required.', 'error');
            title.focus();
            isValid = false;
        } else if (!simplifiedText.value.trim()) {
            showMessage(formMessageContainer, 'Simplified Itinerary is required.', 'error');
            simplifiedText.focus();
            isValid = false;
        }
        // Add more validation rules as needed (e.g., file types, sizes)
        if (isValid && formMessageContainer.style.display === 'block' && formMessageContainer.classList.contains('error')) {
             formMessageContainer.style.display = 'none'; // Hide previous error if current validation passes
        }
        return isValid;
    }


    // --- Handle Delete Itinerary ---
    async function handleDeleteItinerary(event) {
        const itineraryId = event.target.dataset.id;
        if (!itineraryId) return;

        if (confirm('Are you sure you want to delete this itinerary? This action cannot be undone.')) {
            showLoading(true); // Might need a specific loading indicator for delete
            try {
                const response = await fetch(`/api/itineraries/\${itineraryId}`, { method: 'DELETE' });
                const result = await response.json();

                if (response.ok) {
                    showMessage(formMessageContainer || document.querySelector('main'), result.message || 'Itinerary deleted successfully!', 'success'); // Show message in form or main area
                    // If on index page, refresh list. If on detail page, redirect.
                    if (window.location.pathname.includes(`/web/itinerary/\${itineraryId}`)) {
                        setTimeout(() => { window.location.href = '/web/index'; }, 1500);
                    } else {
                        fetchItineraries();
                    }
                } else {
                    showMessage(formMessageContainer || document.querySelector('main'), `Error: \${result.error || 'Failed to delete itinerary'}`, 'error');
                }
            } catch (error) {
                console.error('Error deleting itinerary:', error);
                showMessage(formMessageContainer || document.querySelector('main'), 'An unexpected error occurred during deletion.', 'error');
            } finally {
                showLoading(false);
            }
        }
    }

    // Update Nav link active state based on current page (simple example)
    const currentPath = window.location.pathname;
    document.querySelectorAll('nav .nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath || (currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/web/')) {
            // Check if currentPath starts with link's href, but ensure it's not just the base '/web/' matching everything.
            // For example, if link is '/web/itineraries/add' and currentPath is '/web/itineraries/add', it's a match.
            // If link is '/web/index' (or similar for browse) and currentPath is '/web/' or '/web/index', it's a match.
            if (link.getAttribute('href').endsWith('/web/index') && currentPath === '/web/') { // Handle root redirect explicitly
                 link.classList.add('active');
            } else if (currentPath.startsWith(link.getAttribute('href')) && (link.getAttribute('href').length > currentPath.length - (currentPath.endsWith('/') ? 1:0) || link.getAttribute('href') === currentPath)) {
                 // More precise matching for partial paths, e.g. /web/itinerary/ should not make /web/itineraries/add active
                 link.classList.add('active');
            }

        }
    });
    // A simpler active link logic for the two main links:
    const browseLink = document.querySelector('nav .nav-links a[href*="web/index"]');
    const addLink = document.querySelector('nav .nav-links a[href*="web/itineraries/add"]');

    if (browseLink) browseLink.classList.remove('active'); // Reset
    if (addLink) addLink.classList.remove('active'); // Reset

    if (currentPath.includes('/web/itineraries/add')) {
        if (addLink) addLink.classList.add('active');
    } else if (currentPath.includes('/web/itinerary/') || currentPath.endsWith('/web/') || currentPath.endsWith('/web/index')) {
        // Any other page related to browsing/viewing defaults to "Browse" active
        if (browseLink) browseLink.classList.add('active');
    }


});
