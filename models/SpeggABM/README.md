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


> [!NOTE]
> To understand how `SIR` model is structured at a deeper level, it is necessary to break down each class in that project.

### `SIR` classes breakdown
#### `Vector` class in [`/include/vector.py`](include/vector.py)

This is the class that contains a field indicating `x` position and another indicating the `y` position. Basic operations like addition, subtraction, multiplication, and division, even absolute value are overriden to work with other `Vector` objects.

#### `Agent` class in [`models/SIR/ensemble_training/ABM.py`](models/SIR/ensemble_training/ABM.py)

This class abstracts a moving agent within an epidemiological population. Each instance of this class has a `Vector` indicating their locations in space, as well as its movement within space is also dictated by these three methods:

- `repel_from_wall(self, direction: Vector, space: Union[Vector, Sequence])`: Moves along the direction, but bounces back if hits the boundaries.
- `move_in_periodic_space(self, direction: Vector, space: Union[Vector, Sequence])`: Moves in the periodic space, its meaning is vague for now but the key idea is that they have to move somehow.
- `move_randomly_in_space(...)`: Arguments are not shown here. Moves the agent normally randomly.

#### `SIR_ABM` class in [`models/SIR/ensemble_training/ABM.py`](models/SIR/ensemble_training/ABM.py)

This class simulates a population of `Agent`s, whose main attributes include:

- `kinds: dict[int, dict[int, None]]`: Tracks indices of susceptible, infected, and recovered `Agent`s.
- `current_kinds: list[int]`: Size is number of agents, tracks SIR status for each.
- `current_counts: torch.tensor`: Size is 3, counts how many agents of each category of SIR.

Here are the main events in the simulation:

1. Assume the first agent in the population is the first infectious one. Set all other agents to susceptible kinds.
2. Move agents randomly in space.
3. Calculate the distance of susceptible agents to infectious ones, then apply the infectious likelihood to determine what among those susceptible ones are going to be next infectious agents:
      - Number of contacts is calculated as:

      $$
      NC = \sum_{i=0}^{S(t)} : \sum_{j=0}^{I(t)} \text{ceil}(\max(1 - \frac{d_{ij}}{r}, 0))
      $$

      with S, I as number of susceptible and infected agents, respectively; d as the distance between 2 agents; r as the radius needed for infection to happen.

      - Determine if susceptible agents turn infectious:

      $$
      IST = \sum_{i=0}^{S(t)} : \text{ceil}(\max((1 - p)^{NC} - \sigma, 0))
      $$

      where p is the infected probability; $\sigma$ as a uniformly random number.

      - From $IST$, take indices of all elements that are non-zero. Those indices are those of susceptible agents which will turn infectious.
      - Update those susceptible into infectious.
      - For recovering state, any infected agents that have gone through enough time steps specified by `t_infectious` will turn recovered, thus being transferred to the recovered category.

#### [`DataGeneration.py`](models/SIR/ensemble_training/DataGeneration.py)

This file provides utility functions to generate training datasets as well as prepare `h5` groups and storage. These functions include:

1. **`generate_data_from_ABM()`**:
This mainly takes in three tensors for positions `(time_steps, N_agents)`, kinds `(time_steps, N_agents)`, and counts `(time_steps, 3)` across all time steps. It will run the `SIR_ABM` simulation and after every time step, it will gradually append current information about the simulated population to the three tensors described above. It will also append the density, aka percentage of susceptible-infected-recovered agents out of the population.

2. **`generate_smooth_data()`**:
Instead of generating training dataset from simulation, this will generate data by solving a system of stochastic differential equations.

      Here is the description of how it works:

      $$
      \begin{bmatrix}
      \frac{dS(t)}{dt} \\ \frac{dI(t)}{dt} \\ \frac{dR(t)}{dt}
      \end{bmatrix} = 
      \begin{bmatrix}
            -\beta & -\sigma \cdot w \\
            \beta & -\tau + \sigma \cdot w \\
            0 & \tau
      \end{bmatrix}
      \times
      \begin{bmatrix}
            S(t) \cdot I(t) \\ I(t)
      \end{bmatrix}
      $$

      $\beta$ is the infection rate, $\tau$ is the recovering rate, $\sigma$ is random noise, $w$ is a normal distribution $N(0, 1)$. with one constraint that if these values exceed below 0 or over 1, clip those to only 0 or 1. The training data is also density, or proportion of S-I-R agents out of the population.

3. **`get_SIR_data()`**:
Either returns training dataset from simulation or ODE based on user's configuration.

Also, one role of this `DataGeneration.py` is that all its functions receive a premature `h5` object and then fill it up with necessary attributes such as `coords`,... so that the neural network training process can write training information into it after each epoch.

#### `SIR_NN` in [`models/SIR/ensemble_training/NN.py`](models/SIR/ensemble_training/NN.py)

This class uses one of the [base models](include/base_model.py), which contains multiple simple linear layers organized sequentially, to train and make prediction of three parameters, probability of infection $\beta$, time of infection $t$, and noise $\sigma$.

Per epoch, the training dataset is processed in batches, meaning if there is a parallelizable computer, it will cut the datasets into multiple batches and will process one batch after another. Say that the batch size is 5, so that parallelizable computer will process through the dataset 5 times per epoch.

The training dataset is passed into the neural network so the calculation gets funneled down to just a three-element tensor: $\beta$, $t$, and $\sigma$. With necessary scaling, this is the final prediction of three parameters in `SIR` model. These three predicted parameters are then used to solve a system of ODE as described in `generate_smooth_data()`, and then we will have a predicted epidemic progression in population, which can be used to compare against the training dataset (also containing real or simulated epidemic progression) and calculate the loss value.

> [!NOTE]
> `current_density` as in neural network module is pulled from the training dataset, which I described as proportions of S-I-R agents out of the population.

After each epoch, the `write_data()` method will write current predicted parameters ($\beta$, $t$, and $\sigma$), and current loss into the defined `h5` group, ready for plotting.

## Application - How that workflow can be translated to sPEGG

This will be done later because there are still progresses later on to determine what parameters are and how these should be trained. However, there is one thing that may be different with this `SIR` approach, which we might see that our sPEGG ABM also serves as another layer in the Neural Network, but another direction could be to use sPEGG as a data generator, then we start to train NN to learn the underlying parameters that have driven the evolutionary process.
