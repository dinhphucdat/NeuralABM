# Import system-level library
import os, sys
import torch
import numpy as np
from _collections_abc import Iterable

# Import the simulation module
# Path to the simulation module
SIMULATION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "GenotypeDiffFecundity"
)
# Append the shared object to the system's path
sys.path.append(
    os.path.join(SIMULATION_PATH, "build")
)

# Import the simulation module
from GenotypeDiffFecundity import simulate

from .DataGeneration import *
from .ABM import *
from .NN import *
