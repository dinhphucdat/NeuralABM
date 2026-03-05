# Optimization Hub For sPEGG Simulation Model
## Primer - Describe how other models work

For the purpose of demonstration, the SIR model is going to be chosen.

### Folder structure and meaning

This model has four major YAML configuration files, including:

- `SIR_info`: the heart of the `utopya` tool, needed to define the workflow of the NeuralABM's execution.
- `SIR_cfg`: containing parameters needed to run both Agent-Based Model and the Neural Network model. Such parameters are determined within the script written for the actual ABM or NN models (i.e. `run.py`).
- `SIR_base_plots`: Defining the plot types that this project bases on. Will be used when the workflow steps into the plotting process. This also specifies which parameters to plot, so it is important to save data into `h5` groups properly when executing the Simulation and Neural Net models. This configuration file specifies the structure of the data to plot within the `h5` groups that the models created when being run.
- `SIR_plots`: An extension of the base plots configuration. **_To be continued..._**

### How Agent-Based Simulation and Neural Net Models intertwine with each other

There is a `SIR_ABM` Agent-Based simulation model that simulates the movement of agents in some free space. Then, the `DataGenerator` generates the training dataset through the `SIR_ABM` to simulate the life cycles of agents and then record the activities into training data. The `SIR_NN` Neural Network model takes some initial parameters and optimizes those based on the training data generates through the Agent-Based Simulation. The `Langevin` appears to be a Monte-Carlo Markov Chain sampler, whose purpose is unintelligible for now.

The `h5` group mentioned acts as a data buffer where Neural Net model writes some data into it after every training epoch. That writing activity can be seen in the `write_data()` method in the `SIR_NN` class. So, essentially, epoch-wise data will be completed as soon as the training finishes, only after which the plotting operation accesses such data.

The workflow graph looks like:

```
SIR_ABM → DataGenerator → Training Data
                    ↓
              SIR_NN (training) → Epoch data → h5 file
                    ↓
            Langevin Sampler → Parameter distributions → h5 file
                    ↓
              Plotting (SIR_plots.yml)

```

`Langevin` isn't just an MCMC sampler for plotting - it's specifically for Bayesian uncertainty quantification after training. It generates parameter distributions to show confidence intervals around learned values like infection rates. There is a configuration parameter that determines if this sampling process should take place.

### How the parameters are trained

The neural network model used was prepared beforehand in the `/include/` directory, which then is imported into the `NN.py` of the `SIR` project.

After the simulation finishes, we want to know the underlying parameters that drive the epidemic status in that direction. In this context, those are three parameters, including `p_infect`, `t_infect`, and `sigma`. Hidden weights and layers of a neural network are used to predict those three parameters, which then are projected for each epoch, as can be seen in the plots.

So in conclusion, the simulation generates a case dataset ascribed to an infectious population, which is then used to train a neural network to figure out what the three underlying parameters that might have driven the epidemic dynamics were. The training progress will record those three parameters' predictions after each epoch.

```
ABM Simulation → Case dataset → Want to learn p, t, sigma
                                          ↓
                                    NN : hidden layers, 
                                          activation functions
                                          ↓
                                      Optimize
                                          ↓
                                     Predicted p, t, sigma
```

## Application - How that workflow can be translated to sPEGG

This will be done later because there are still progresses later on to determine what parameters are and how these should be trained. However, there is one thing that may be different with this `SIR` approach, which we might see that our sPEGG ABM also serves as another layer in the Neural Network, but another direction could be to use sPEGG as a data generator, then we start to train NN to learn the underlying parameters that have driven the evolutionary process.
