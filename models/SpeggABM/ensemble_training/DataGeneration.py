import subprocess
from ensemble_training import *

out = subprocess.run(["./setup_spegg.sh"],cwd="..", capture_output=True, text=True)


def process_output(output : str, delimiter : str = "\t") -> list:
    lines = output.strip().split("\n")
    data = []
    for line in lines:
        values = line.split(delimiter)
        data.append([float(v) if is_float(v) else v for v in values])
    return data
