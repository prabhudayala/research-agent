# Multi-Agent Research System

This project implements an **Automated Market Research & Report System** using a team of AI agents to plan, research, write, and review content. It includes a **React Frontend** for interaction.

## System Overview

The application is built with:
- **Python 3.9+**
- **OpenAI API** (GPT-3.5/4)
- **FastAPI** for the service layer
- **React (Vite)** for the User Interface
- **DuckDuckGo** for web search
- **Docker & Kubernetes** for deployment

### Architecture
1. **Frontend**: React app serving the UI.
2. **Backend**: FastAPI app managing the Agent Orchestrator.
3. **Agents**: Planner, Researcher, Writer, Reviewer.

## Project Structure

```
├── app/                # Backend logic
├── ui/                 # Frontend React App (Vite)
├── scripts/            # CLI Tools
├── k8s/                # Kubernetes manifests
├── Dockerfile          # Backend Dockerfile
└── requirements.txt
```

## How to Run

### 1. Local Python (Backend Only)
Ensure you have the virtual environment and `.env` set up.

```bash
# Activate venv
.\venv\Scripts\activate

# Run the CLI demo
python scripts/demo.py

# Run the API
uvicorn app.main:app --reload
```

### 2. Kubernetes (Minikube) Setup

1.  **Start the Cluster**:
    ```powershell
    minikube start --driver=docker
    ```

2.  **Deploy Both Services**:
    ```bash
    # Create the secret for your API key
    kubectl create secret generic openai-secret --from-literal=api-key=YOUR_ACTUAL_API_KEY_HERE
    
    # Apply backend manifests
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml

    # Apply frontend manifests
    kubectl apply -f k8s/frontend-deployment.yaml
    kubectl apply -f k8s/frontend-service.yaml
    ```

3.  **Access the App**:
    ```powershell
    # Get Backend URL
    minikube service research-agent --url

    # Get Frontend URL (Open this in browser!)
    minikube service research-ui --url
    ```

## Operations

### Updating the API Key (Configuration)
1.  **Delete the old secret**: `kubectl delete secret openai-secret`
2.  **Create the new secret**: `kubectl create secret generic openai-secret --from-literal=api-key=YOUR_NEW_KEY`
3.  **Restart the Backend**: `kubectl rollout restart deployment research-agent`

### Viewing Logs
- **Backend**: `kubectl logs -l app=research-agent -f`
- **Frontend**: `kubectl logs -l app=research-ui -f`
