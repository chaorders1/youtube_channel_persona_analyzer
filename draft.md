** # Project overview **
The project focuses on YouTube Channel Persona Analysis. It involves building a pipeline to analyze YouTube channel data, exposing this functionality through a simple API using FastAPI, and developing a web application to display the results.


** # Core functionalities **
1. YouTube Channel Persona Analysis
	•	Description: Analyze YouTube channel data to generate insights about the channel’s persona.
	•	Implementation: Implemented in persona_pipeline.py.
2. 	API Development using FastAPI
	•	Description: Build a simple API to expose the persona analysis functionality.
	•	Implementation: Implemented in persona_api.py.
	•	Endpoint:
	•	POST /analyze: Accepts YouTube channel data and returns persona analysis results.
	•	Example Request and Response:
	•	See the Documentation section for detailed examples.
    - Code example in persona_api.py

    # Example curl request

    curl -X POST http://localhost:8001/test-analyze \
        -H "Content-Type: application/json" \
        -d '{
            "youtube_channel_url": "https://www.youtube.com/@AIJasonZ"
        }'

3. Web Application for Result Display
	•	Description: Develop a simple web app to display the analysis results.
	•	Implementation: Interfaces with the API to fetch and display data to users.
	•	Features:
	•	User-friendly interface for inputting YouTube channel details.
	•	Displays persona analysis in an organized format.
    # Example web app command
    uvicorn web_app.main:app --reload --port 8000


** # Doc **
xxxxx
*** libraries
The project utilizes the following libraries:
	•	FastAPI: For building the API.
	•	Uvicorn: ASGI server for running the FastAPI app.
	•	Requests: To handle HTTP requests.
	•	Jinja2: For templating in the web app.
	•	Pandas/Numpy: For data analysis in persona_pipeline.py.
	•	Other Dependencies: Listed in requirements.txt.
*** api code example

** # Current file structure **
.
├── LICENSE
├── data
│   ├── crop_AIJasonZ_20241106_130942
│   ├── crop_AIJasonZ_20241106_130942_analysis.md
│   └── web_snapshots
├── draft.md
├── load_env.sh
├── requirements.txt
├── persona_api.py
├── utility
│   ├── data
│   ├── persona.py
│   ├── persona_pipeline.py
│   ├── picture_crop.py
│   └── screenshotapi.py
└── web_app
    ├── main.py
    ├── templates
    │   └── index.html
    └── static
        ├── css
        │   └── style.css
        └── js
            └── script.js

** # Additional requirements **
	•	Lean Structure: Keep the project as lean as possible with minimal files and dependencies.
	•	Documentation:
	•	Include docstrings and comments in the code for clarity.
	•	Provide a README.md with setup instructions.
	•	Environment Setup:
	•	Use load_env.sh to set environment variables if necessary.
	•	All dependencies should be listed in requirements.txt.
	•	Code Quality:
	•	Follow best practices for code formatting and structure.
	•	Ensure code is modular and functions are reusable.
	•	Testing:
	•	Write basic tests to verify that the API endpoints and web app function correctly.
	•	Version Control:
	•	Use Git for version control.
	•	Make clear and descriptive commit messages.

** # Future Enhancements (Optional) **
xxxxx