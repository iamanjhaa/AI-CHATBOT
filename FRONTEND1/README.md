# SIH26043 Frontend

Vanilla HTML, CSS, and JavaScript frontend for Phase 1 of the SIH26043 problem solving chatbot.

## Run

Open `index.html` in a browser, or serve the folder with a simple static server:

```bash
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500
```

## Backend Requirement

Start the FastAPI backend first:

```bash
cd ../BACKEND
uvicorn app.main:app --reload
```

The frontend expects the backend at:

```text
http://127.0.0.1:8000/chat
```
