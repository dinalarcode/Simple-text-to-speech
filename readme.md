# OpenAI Text-to-Speech Web App

A simple web app that turns your text into natural-sounding speech using the OpenAI API. You can choose from 10 different voices, set the tone or style, and download the result as MP3 or WAV.

---

## Before You Start

Make sure you have these installed on your computer:

- Python 3.9 or newer — download from https://www.python.org/downloads
- Git — download from https://git-scm.com/downloads
- Visual Studio Code — download from https://code.visualstudio.com
- An OpenAI API key — get one at https://platform.openai.com/api-keys

---

## Setup Guide

### Step 1 — Clone the project

Open VS Code, then open the terminal by going to the top menu and clicking Terminal, then New Terminal.

In the terminal, run:

```
git clone https://github.com/dinalarcode/Simple-text-to-speech.git
cd Simple-text-to-speech
```

After that, open the project folder in VS Code by running:

```
code .
```

### Step 2 — Create a virtual environment

In the VS Code terminal, run:

```
python -m venv venv
```

Then activate it.

On Windows:
```
venv\Scripts\activate
```

On Mac or Linux:
```
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal line. That means it is active.

If VS Code shows a popup asking "Do you want to select this environment for the workspace?", click Yes.

### Step 3 — Install the required packages

In the terminal, run:

```
pip install -r requirements.txt
```

This installs Flask, the OpenAI SDK, and a few other small libraries the app needs.

### Step 4 — Add your OpenAI API key

In the VS Code file explorer on the left side, you will see a file called `.env.example`. Right-click it and select Copy, then right-click in the same folder and select Paste. Rename the copied file to `.env`.

Open the `.env` file and replace the placeholder with your actual key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

Save the file with Ctrl+S (or Cmd+S on Mac). Keep this key private and never share it.

### Step 5 — Run the app

In the terminal, run:

```
python app.py
```

You will see something like:

```
Running on http://127.0.0.1:5000
```

Hold Ctrl and click that link to open it in your browser, or just copy and paste it into your browser's address bar.

---

## How to Use

1. Type or paste the text you want to hear in the first box.
2. Optionally, add a voice instruction in the second box, for example: "Speak slowly and in a calm tone."
3. Choose a voice from the dropdown menu.
4. Choose MP3 or WAV as the output format.
5. Choose the model. Use gpt-4o-mini-tts for speed, or gpt-4o-tts for the best quality.
6. Click Generate Speech.
7. The audio will play automatically. Click Download to save it to your computer.

---

## Project Files

```
Simple-text-to-speech/
    app.py              Flask backend and API endpoint
    requirements.txt    Python packages needed
    .env.example        Template for your API key
    agent.md            How the app was built
    readme.md           This file
    static/
        style.css       Stylesheet
    templates/
        index.html      The web page
```

---

## Common Issues

If the app shows a warning about OPENAI_API_KEY not being set, make sure your .env file exists and contains the correct key.

If you get a 401 error, your API key is invalid or has no credit. Check your OpenAI account.

If port 5000 is already in use, open app.py in VS Code and change the port number at the bottom of the file.

To stop the app, click on the terminal in VS Code and press Ctrl+C.

---

## License

This project is for personal and educational use. The OpenAI API is subject to OpenAI's usage policies at https://openai.com/policies/usage-policies.
