document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#analysisForm');
    const urlInput = document.getElementById('youtube_channel_url');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');
    const resultsContainer = document.querySelector('.results-container');

    const stages = [
        { message: "Initializing analysis...", progress: 10, duration: 7000 },
        { message: "Capturing channel screenshots...", progress: 30, duration: 7000 },
        { message: "Processing images...", progress: 50, duration: 5000 },
        { message: "Analyzing channel content...", progress: 70, duration: 4000 },
        { message: "Generating persona report...", progress: 90, duration: 3000 },
        { message: "Finalizing results...", progress: 95, duration: 2000 }
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
            if (currentStage < stages.length) {
                clearInterval(progressInterval);
                progressInterval = setInterval(simulateProgress, stages[currentStage].duration);
            }
        }
    }

    function startNewAnalysis() {
        // 1. Hide any existing results
        const existingResults = document.querySelector('.results-container');
        if (existingResults) {
            existingResults.remove();
        }

        // 2. Reset and show progress bar
        currentStage = 0;
        progressBar.style.width = '0%';
        progressBar.style.backgroundColor = 'var(--secondary-color)';
        progressStatus.style.color = 'var(--text-color)';
        progressStatus.textContent = 'Initializing analysis...';
        progressContainer.style.display = 'block';

        // 3. Start progress simulation
        progressInterval = setInterval(simulateProgress, stages[0].duration);
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validate input
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

        // Start new analysis
        startNewAnalysis();

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

            // Stop progress simulation
            clearInterval(progressInterval);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Show completion
            updateProgress("Analysis complete!", 100);
            await new Promise(resolve => setTimeout(resolve, 500));

            // Hide progress
            progressContainer.style.display = 'none';

            // Update page content
            const result = await response.text();
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = result;

            // Extract and append only the results container
            const newResults = tempDiv.querySelector('.results-container');
            if (newResults) {
                document.querySelector('.container').appendChild(newResults);
            }

            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = 'Analyze Channel';

        } catch (error) {
            clearInterval(progressInterval);
            console.error('Error:', error);
            progressStatus.textContent = 'Error: ' + error.message;
            progressStatus.style.color = 'var(--error-color)';
            progressBar.style.backgroundColor = 'var(--error-color)';
            
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = 'Analyze Channel';
        }
    });
}); 