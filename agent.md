# Agent Build Process and Architecture

## Overview

This document explains the decisions made when building the OpenAI Text-to-Speech web application and describes how the different parts of the app work together.

---

## Design Decisions

### Backend Framework

Flask was chosen as the backend framework because it is lightweight and simple. The app only needs to handle one route that accepts text and returns audio, which is a good fit for Flask. It also has built-in support for sending binary file responses, which is what we need for returning audio data.

### Frontend

The frontend is a single HTML file with a small amount of JavaScript and a separate CSS file. No frontend frameworks like React or Vue were used, keeping the project easy to understand and run without any build tools.

### Voice Instructions

When a user fills in the voice instructions field, the text is passed directly to the OpenAI API using the instructions parameter. This tells the model how to speak, for example with a certain tone or accent. If the field is left empty, the parameter is simply not sent.

### Audio Handling

The audio returned by OpenAI is stored temporarily in memory and sent straight to the browser. No audio files are saved to disk, which means there is no cleanup needed and the app stays lean.

### Model Choices

Two models are available:

- gpt-4o-mini-tts is fast and handles voice instructions well. It is the default.
- gpt-4o-tts produces the highest quality audio and also supports voice instructions fully.

---

## Architecture

```
Simple-text-to-speech/
    app.py              Flask backend and API endpoint
    requirements.txt    Python packages needed
    .env.example        Template for environment variables
    agent.md            This file
    readme.md           User setup and usage guide
    static/
        style.css       Stylesheet
    templates/
        index.html      Frontend page
```

### How a Request Works

1. The user fills in the form and clicks Generate Speech.
2. The browser sends the form data as JSON to the /api/tts endpoint.
3. Flask receives the data, validates it, and calls the OpenAI audio API.
4. OpenAI returns the audio bytes, which Flask streams into memory.
5. Flask sends the audio back to the browser.
6. The browser plays the audio and enables the download link.

### Core Principles

- Audio is never written to disk.
- All inputs are validated on the server before calling the API.
- Errors from the API are caught and shown to the user in a readable way.
- The API key is read from environment variables and never stored in the code.

---

## Possible Future Improvements

- Add rate limiting so the app cannot be abused if made public.
- Add caching so the same request does not call the API twice.
- Support longer texts by splitting them into chunks before sending to the API.
- Stream audio to the browser in real time instead of waiting for the full file.
