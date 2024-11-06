document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#analysisForm');
    const urlInput = document.getElementById('youtube_channel_url');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');

    const stages = [
        { message: "Initializing analysis...", progress: 10 },
        { message: "Capturing channel screenshots...", progress: 30 },
        { message: "Processing images...", progress: 50 },
        { message: "Analyzing channel content...", progress: 70 },
        { message: "Generating persona report...", progress: 90 },
        { message: "Finalizing results...", progress: 95 }
    ];

    let currentStage = 0;
    let progressInterval;

    function updateProgress(stage, percentage) {
        progressBar.style.width = `${percentage}%`;
        progressStatus.textContent = stage;
    }

    function simulateProgress() {
        if (currentStage < stages.length) {
            updateProgress(stages[currentStage].message, stages[currentStage].progress);
            currentStage++;
        }
    }

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

        // Show progress container and start progress updates
        progressContainer.style.display = 'block';
        currentStage = 0;
        progressInterval = setInterval(simulateProgress, 3000); // Update every 3 seconds
        
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

            // Clear the progress interval
            clearInterval(progressInterval);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Update to 100% before showing results
            updateProgress("Analysis complete!", 100);
            await new Promise(resolve => setTimeout(resolve, 500)); // Brief pause
            
            // Load results
            const result = await response.text();
            document.documentElement.innerHTML = result;
            
            // Reinitialize the script
            const script = document.createElement('script');
            script.src = '/static/js/script.js';
            document.body.appendChild(script);

        } catch (error) {
            clearInterval(progressInterval);
            console.error('Error:', error);
            progressStatus.textContent = 'Error: ' + error.message;
            progressStatus.style.color = 'var(--error-color)';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Analyze Channel';
        }
    });
}); 