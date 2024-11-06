document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#analysisForm');
    const urlInput = document.getElementById('youtube_channel_url');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (!urlInput.value.trim()) {
            alert('Please enter a YouTube channel URL');
            return;
        }

        try {
            new URL(urlInput.value);
        } catch (err) {
            alert('Please enter a valid URL');
            return;
        }

        // Show progress container
        progressContainer.style.display = 'block';
        
        // Disable submit button
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Analyzing...';

        try {
            // Submit the form
            const formData = new FormData(form);
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Redirect to the results page with the response
            const result = await response.text();
            document.documentElement.innerHTML = result;
            
            // Reinitialize the script after content update
            const script = document.createElement('script');
            script.src = '/static/js/script.js';
            document.body.appendChild(script);

        } catch (error) {
            console.error('Error:', error);
            progressStatus.textContent = 'Error: ' + error.message;
            progressStatus.style.color = 'var(--error-color)';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Analyze Channel';
        }
    });
}); 