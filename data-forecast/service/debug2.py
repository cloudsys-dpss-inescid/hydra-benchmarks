import subprocess
import os
import sys
import pickle
import shutil
import multiprocessing
from concurrent.futures import ThreadPoolExecutor



docker_command = [
    "docker", "run", "--rm", "--gpus", "all",
    "-v", "/home/claudiocorreia/work/hydra/benchmarks/data-forecast:/data-forecast",
    #"-v", f"{traces_dir}:/app/traces_dir",
    #"-v", f"{models_dir}:/app/models_dir",
    #"-w", "/data-forecast/service",
    "-w", "/data-forecast/service",
    "timeseries-predictor-image",
    #"ubuntu",
    "python3", "debug3.py", "hello back"
]

result = subprocess.run(docker_command, capture_output=True, text=True)


print(result.stdout)

#docker run -it -v /home/claudiocorreia/work/hydra/benchmarks/data-forecast:/inception ubuntu