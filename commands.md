# Research Agent - Commander's Cheat Sheet

Here are the commands you need to manage your application.

## 1. 🚀 Startup Sequence (Do this first)
> **Prerequisite**: Make sure **Docker Desktop** is running!

```powershell
# 1. Start the Cluster (if not running)
minikube start

# 2. Check if everything is running
kubectl get pods

# 3. Access the Frontend UI (Research App)
# This will output a URL like http://127.0.0.1:xyz. Open it.
minikube service research-ui --url
```

## 2. 🛠️ Troubleshooting & Logs
Is something broken? Check the logs.

```powershell
# Check Backend Logs
kubectl logs -l app=research-agent --tail=50 -f

# Check Frontend Logs
kubectl logs -l app=research-ui --tail=50 -f

# Check Database Content (Run inside backend pod)
kubectl exec deployment/research-agent -- python -c "from app.core.db import get_session, User, Report, engine; from sqlmodel import Session, select; session=Session(engine); print(session.exec(select(User)).all());"
```

## 3. 🚢 DevOps (ArgoCD & Jenkins)

```powershell
# Access ArgoCD UI
# Username: admin
# Password: (Run command below to get it)
minikube service argocd-server -n argocd --url

# Get ArgoCD Password
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("UTF5NTdYdXVaLXhkMkRTbg=="))
```

## 4. 🛑 Shutdown
Done for the day?

```powershell
minikube stop
# or to fully delete the cluster
# minikube delete
```
