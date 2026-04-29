import sys
from os.path import dirname as up
import h5py as h5
import numpy as np
import torch
from ensemble_training import *

class Trend:
    def __init__(
            self, h5group : h5.Group, 
            n_parameters, 
            name_parameters, 
            true_records, 
            loss_func, 
            ntime_steps,
            num_interval=50
        ):
        self.h5group = h5group
        self.num_interval = num_interval

        self.xs = np.linspace(0, 1, num_interval)

        self.x_values = self.h5group.create_dataset(
            name = 'x_values',
            shape = (num_interval,),
            maxshape = (None,),
            chunks = True,
            compression = 3
        )
        self.x_values[:] = self.xs[:]

        self.n_parameters = n_parameters
        self.name_parameters = name_parameters

        self.y_values = self.h5group.create_dataset(
            name = 'y_values', 
            shape = (num_interval, n_parameters), 
            chunks = True,
            compression = 3
        )
        self.y_values.attrs["dim_names"] = ["batch", "parameter"]
        self.y_values.attrs["coords_mode__parameter"] = "values"
        self.y_values.attrs["coords__parameter"] = name_parameters

        self.true_records = true_records
        self.loss_func = loss_func
        self.ntime_steps = ntime_steps

    def fill_values(self):
        for i in range(self.n_parameters):
            params = np.full(shape = self.n_parameters, fill_value = 0.5)
            for j, val in enumerate(self.xs):
                copied_params = params.copy()
                copied_params[i] = val
                result = ABM.apply(torch.tensor(copied_params), self.true_records, 0, self.ntime_steps, self.loss_func, 0.01)
                self.y_values[j, i] = result
