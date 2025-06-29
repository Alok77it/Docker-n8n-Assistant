from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import docker
import os
import docker

# 🚫 Clear broken Docker environment overrides
for var in ["DOCKER_HOST", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"]:
    os.environ.pop(var, None)

# ✅ Explicitly set the correct socket (for Linux)
DOCKER_SOCKET = "unix://var/run/docker.sock"

try:
    client = docker.DockerClient(base_url=DOCKER_SOCKET)
    client.ping()
    print("✅ Connected to Docker via UNIX socket")
except Exception as e:
    raise RuntimeError(f"❌ Docker connection failed: {e}")


app = FastAPI()

# Use Unix socket (Linux)
client = docker.DockerClient(base_url="unix://var/run/docker.sock")


# ---------------- Container Management ---------------- #

@app.get("/containers")
def list_containers(all: Optional[bool] = False):
    try:
        containers = client.containers.list(all=all)
        return [
            {
                "id": c.short_id,
                "name": c.name,
                "status": c.status,
                "image": c.image.tags
            } for c in containers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list containers: {str(e)}")


@app.post("/start/{container_id}")
def start_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.start()
        return {"message": f"Container {container_id} started successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start container: {str(e)}")


@app.post("/stop/{container_id}")
def stop_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {"message": f"Container {container_id} stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop container: {str(e)}")


@app.post("/restart/{container_id}")
def restart_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.restart()
        return {"message": f"Container {container_id} restarted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart container: {str(e)}")


@app.delete("/remove/{container_id}")
def remove_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        return {"message": f"Container {container_id} removed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove container: {str(e)}")


@app.get("/logs/{container_id}")
def get_logs(container_id: str, tail: int = 100):
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=tail).decode("utf-8")
        return {"id": container_id, "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


# ---------------- Image Management ---------------- #

@app.get("/images")
def list_images():
    try:
        images = client.images.list()
        return [
            {
                "id": i.short_id,
                "tags": i.tags,
                "size_MB": round(i.attrs["Size"] / (1024 * 1024), 2)
            } for i in images
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")


# ---------------- Run New Container ---------------- #

class RunContainerRequest(BaseModel):
    image: str
    name: Optional[str] = None
    command: Optional[str] = None
    detach: bool = True
    ports: Optional[Dict[str, str]] = None
    environment: Optional[Dict[str, str]] = None


@app.post("/run")
def run_container(config: RunContainerRequest):
    try:
        container = client.containers.run(
            image=config.image,
            name=config.name,
            command=config.command,
            detach=config.detach,
            ports=config.ports,
            environment=config.environment
        )
        return {"message": "Container started", "id": container.short_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run container: {str(e)}")


# ---------------- Docker Info ---------------- #

@app.get("/info")
def get_docker_info():
    try:
        return client.info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Docker info: {str(e)}")

