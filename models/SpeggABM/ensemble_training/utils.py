from ensemble_training import *

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False