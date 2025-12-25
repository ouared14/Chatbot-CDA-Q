# AskLAQ2 - Local Q&A System

## Overview
AskLAQ2 is a local question-answering system that runs completely offline on your machine. It uses sentence embeddings to find the most relevant answers from your dataset.

## System Requirements
- Windows 7/8/10/11, macOS, or Linux
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Python 3.8 or higher

## Installation

### Option 1: Using the Installer (Windows)
1. Double-click `install.bat`
2. Follow the on-screen instructions

### Option 2: Manual Installation
1. Ensure Python 3.8+ is installed
2. Open terminal/command prompt in this folder
3. Run: `pip install -r requirements.txt`

## Running the Application

### Windows:
- Double-click `AskLAQ2.exe`
- OR Run `launch_app.py` with Python

### Mac/Linux:
- Open terminal in this folder
- Run: `python launch_app.py`

## Application Structure
- `app.py` - Main Flask application
- `gradio_app.py` - Gradio interface wrapper
- `launch_app.py` - Application launcher
- `dataset_2026.csv` - Your dataset
- `embeddings_questions.pt` - Pre-computed embeddings
- `user_interactions.json` - User interaction log
- `templates/index.html` - Web interface
- `static/script.js` - Frontend JavaScript

## How to Use
1. Launch the application
2. A browser window will open automatically
3. Type your question in the input box
4. Click "Get Answer" or press Enter
5. View the response from your dataset

## Troubleshooting

### Application won't start:
- Ensure all files are in the same folder
- Check if Python is installed correctly
- Try running: `python app.py` directly

### No answers returned:
- Check if `dataset_2026.csv` exists
- Verify `embeddings_questions.pt` is in the folder

### Performance issues:
- Close other applications to free memory
- Consider using a smaller dataset

## Updating
To update the dataset:
1. Replace `dataset_2026.csv` with your new file
2. Delete `embeddings_questions.pt` (it will be regenerated)
3. Restart the application

## Support
For issues or questions, please check:
1. Application logs in the terminal
2. `user_interactions.json` for error history
3. Ensure all required files are present

## Version: 1.0.0
© 2024 AskLAQ2 Application
