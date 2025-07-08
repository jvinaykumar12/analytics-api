from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.events.schema import EventSchema
import os
import docker
from pydantic import BaseModel
from typing import List

KERNELS_DIR = "./docker/kernels"
router = APIRouter()

def create_kernel_files(kernel_name:str, packages: list[str]):
    kernel_path = os.path.join(KERNELS_DIR, kernel_name)
    os.makedirs(kernel_path, exist_ok=True)
    
    req_path = os.path.join(kernel_path, "requirement.txt")
    with open(req_path, 'w') as f:
        f.write("\n".join(packages))
        
    install_lines = [
        "#!/bin/bash",
        f"conda create -y -n {kernel_name} python=3.11",
        f"/opt/conda/envs/{kernel_name}/bin/pip install ipykernel",
        f"/opt/conda/envs/{kernel_name}/bin/pip install --no-cache-dir \\",
        f"    -r /tmp/common-packages.txt \\",
        f"    -r /tmp/{kernel_name}/requirement.txt",
        f"/opt/conda/envs/{kernel_name}/bin/python -m ipykernel install --user --name={kernel_name} --display-name \"{kernel_name}\""
    ]

    install_script = "\n".join(install_lines)
    
    install_path = os.path.join(kernel_path, "install.sh")
    with open(install_path, 'w') as f:
        f.write(install_script)
    os.chmod(install_path, 0o755)
    
    return kernel_path

def generate_dockerfile():
    dockerfile_script = [
        "FROM jupyter/base-notebook",
        "",
        "USER root",
        "RUN apt-get update && apt-get install -y build-essential",
        "",
        "USER $NB_UID",
        'COPY base/common-packages.txt /tmp/',
        ""
    ]
    
    for kernel_name in sorted(os.listdir(KERNELS_DIR)):
        kernel_dir = f"kernels/{kernel_name}"
        dockerfile_script += [
            f"COPY {kernel_dir} /tmp/{kernel_name}",
            f"RUN bash /tmp/{kernel_name}/install.sh",       
            f""
        ]
        
    dockerfile_script += [
        f"USER root",
        "RUN rm -rf /tmp/*",
        "USER $NB_UID"
    ]
    
    with open(DOCKER_FILE_PATH, 'w') as f:
        f.write('\n'.join(dockerfile_script))
        
    return DOCKER_FILE_PATH

docker_client = docker.from_env()


def edit_kernel_files(kernel_name: str, packages: list[str]):
    kernel_path = os.path.join(KERNELS_DIR, kernel_name)
    if not os.path.exists(kernel_path):
        raise FileNotFoundError(f"Kernel '{kernel_name}' does not exist.")

    # Overwrite requirements.txt
    with open(os.path.join(kernel_path, "requirement.txt"), "w") as f:
        f.write("\n".join(packages))

    # No need to re-edit install.sh unless you want to modify naming
    return kernel_path


DOCKER_FILE_PATH = "./docker/Dockerfile"


def build_image_stream():
    def log_generator():
        try:
            # Use the low-level API client for real streaming
            logs = docker_client.api.build(
                path='./docker',
                dockerfile="Dockerfile",
                tag="custom-jupyter:latest",
                rm=True,
                forcerm=True
            )

            # logs is now a generator that yields log entries in real-time
            # We need to decode the JSON manually since decode=True isn't available
            for chunk in logs:
                try:
                    # Parse the JSON chunk
                    import json
                    log_line = json.loads(chunk.decode('utf-8'))
                    print(log_line['stream'])

                    if 'stream' in log_line:
                        yield log_line['stream']
                    elif 'errorDetail' in log_line:
                        yield f"ERROR: {log_line['errorDetail']['message']}\n"
                    elif 'error' in log_line:
                        yield f"ERROR: {log_line['error']}\n"
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If we can't decode, just yield the raw chunk
                    yield chunk.decode('utf-8', errors='ignore')

        except docker.errors.BuildError as e:
            # Handle build errors
            for chunk in e.build_log:
                if 'stream' in chunk:
                    yield chunk['stream']
                elif 'errorDetail' in chunk:
                    yield f"ERROR: {chunk['errorDetail']['message']}\n"
        except Exception as e:
            yield f"Unexpected error: {str(e)}\n"

    return StreamingResponse(log_generator(), media_type="text/plain")


class KernelRequest(BaseModel):
    name: str
    packages: List[str]
    
    
@router.post("/kernels/create")
def create_kernel(req: KernelRequest):
    create_kernel_files(req.name, req.packages)
    generate_dockerfile()
    return build_image_stream()


@router.put("/kernels/edit")
def update_kernel(req: KernelRequest):
    edit_kernel_files(req.name, req.packages)
    generate_dockerfile()
    return build_image_stream()


@router.get("/")
def read_events() -> list[EventSchema]:
    return {
        "items":"test"
    } 

@router.get("/{event_id}")
def get_event(event_id:int) -> EventSchema:
    return {"id": event_id}