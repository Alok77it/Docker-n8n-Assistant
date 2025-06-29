# 🧠 FastAPI Docker Controller + n8n AI Agent (via ngrok)

## Overview

This project enables **natural language control of Docker containers** using an n8n AI Agent that communicates with a FastAPI backend (which interacts with the Docker Engine). FastAPI is exposed securely to the internet using ngrok, allowing external HTTP requests from n8n.

> **Note:**  
> This project will be integrated into the **infracopilot** project.  
> Development is ongoing; this repository is a work in progress.

---

## Architecture

```
User Message
   ↓
n8n AI Agent (OpenAI + Memory)
   ↓
HTTP Request Tool (HTTPS via ngrok)
   ↓
FastAPI (Docker SDK)
   ↓
Docker Engine (via Unix socket)
```

---

## 1. FastAPI Docker Controller

### Project Structure

```
docker-chatbot-assistant/
├── main.py
├── Dockerfile (optional)
├── requirements.txt
└── test.py
```

### main.py

The FastAPI app provides endpoints to:

- **List** all Docker containers
- **Start** a container by ID
- **Stop** a container by ID
- **Get logs** for a container by ID

Endpoints:

- `GET /containers` — List all containers
- `POST /start/{container_id}` — Start a container
- `POST /stop/{container_id}` — Stop a container
- `GET /logs/{container_id}` — Retrieve container logs
---

## 2. Expose FastAPI via HTTPS (ngrok)

Run FastAPI (e.g. with [Uvicorn](https://www.uvicorn.org/)):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Expose it with ngrok:

```bash
ngrok http 8000
```

This provides an HTTPS URL like:

```
https://abc123.ngrok.io
```

You can test with:

```bash
curl https://abc123.ngrok.io/containers
```

---

## 3. n8n Setup

- **Trigger Node**: *When Chat Message Received*
- **AI Agent Node**: Uses OpenAI (or other) + Simple Memory + HTTP Request Tool nodes

### HTTP Request Tool Nodes (for each endpoint):

1. **List Containers**
    - `GET https://abc123.ngrok.io/containers`

2. **Start Container**
    - `POST https://abc123.ngrok.io/start/{{ $json["id"] }}`

3. **Stop Container**
    - `POST https://abc123.ngrok.io/stop/{{ $json["id"] }}`

4. **Get Logs**
    - `GET https://abc123.ngrok.io/logs/{{ $json["id"] }}`

---

## 4. Sample Prompts in n8n Chat

```
- Show all Docker containers
- Start the container named backend
- Stop the nginx container
- Get logs for redis container
```

---

## 5. Deployment Notes

| Component     | Details                                                   |
| ------------- | --------------------------------------------------------- |
| FastAPI       | Uvicorn via `uvicorn main:app --host 0.0.0.0 --port 8000` |
| Docker Access | Uses Unix socket `/var/run/docker.sock`                   |
| Python SDK    | `docker` (installed via `pip install docker`)             |
| ngrok         | Public HTTPS tunnel for FastAPI                           |
| n8n           | Local or Docker with AI Agent enabled                     |

---

## 7. requirements.txt

```
fastapi
uvicorn
docker
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ✅ You're ready!  
You now have a natural-language Docker controller, powered by FastAPI, n8n's AI agent, and secured for external access via ngrok.

---

**Project status: In progress. To be integrated with the infracopilot project.**
