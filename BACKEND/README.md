# SIH26043 Backend

FastAPI backend for Phase 1 of the SIH26043 AI-powered problem solving chatbot.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

## Test

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"problem\":\"My kitchen sink is blocked\"}"
```

## Endpoint

`POST /chat`

Request:

```json
{
  "problem": "My kitchen sink is blocked"
}
```

Response:

```json
{
  "problem": "",
  "severity": "LOW",
  "can_solve_myself": true,
  "solution": [],
  "required_tools": [],
  "estimated_time": "",
  "estimated_cost": "",
  "safety_precautions": [],
  "when_to_stop": "",
  "when_to_contact_authority": "",
  "prevention": []
}
```
