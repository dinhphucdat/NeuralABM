#!/home/wormlab/miniforge3/bin/python3
import logging
from ruamel.yaml import YAML
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ensemble_training import *

from os.path import dirname as up

from dantro._import_tools import import_module_from_path

sys.path.append(up(up(up(__file__))))

base = import_module_from_path(mod_path=up(up(up(__file__))), mod_str="include")

log = logging.getLogger(__name__)

def load_config(config_path : str) -> dict:
    """
    This function will load the configuration from a YAML file and return it as a dictionary.

    :param config_path: The path to the YAML configuration file
    :type config_path: str
    :return: A dictionary containing the configurations
    :rtype: dict
    """
    yaml = YAML(typ='safe')
    cfgs = {}
    with open(config_path, 'r') as f:
        cfgs = yaml.load(f)
    return cfgs

if __name__ == "__main__":
    # Load configurations
    config_file = sys.argv[1]
    overall_cfgs = load_config(config_file)
    model_name = overall_cfgs.get("root_model_name", "SpeggABM")
    log.info(f"   Model name:  {model_name}")
    cfgs = overall_cfgs[model_name]


    # print(training_data)

    # Get the training and neural net config
    training_cfgs = cfgs['Training']
    nn_cfgs = cfgs['NeuralNet']

    # Select the training device and number of threads to use
    device = nn_cfgs.get("device", None)
    if device is None:
        device = (
            "mps"
            if torch.backends.mps.is_available()
            else "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
    num_threads = nn_cfgs.get("num_threads", None)
    if num_threads is not None:
        torch.set_num_threads(num_threads)
    log.info(
        f"   Using '{device}' as training device. Number of threads: {torch.get_num_threads()}"
    )

    # Get the random number generator
    log.info("   Creating global RNG ...")
    rng = np.random.default_rng(training_cfgs["seed"])
    np.random.seed(training_cfgs["seed"])
    torch.random.manual_seed(training_cfgs["seed"])

    log.info(f"   Creating output file at:\n        {overall_cfgs['output_path']}")
    h5file = h5.File(overall_cfgs["output_path"], mode="w")
    h5group = h5file.create_group(model_name)

        # Get the Training config, initialize training data generation
    data_gen_cfgs = cfgs['Data']
    # Generate training data
    training_data = generate_training_data(
        data_gen_cfgs
    ).to(device)

    # Initialise the neural net
    log.info("   Initializing the neural net ...")

    # Initialize the neural network object
    net = base.FeedForwardNN(
        input_size=data_gen_cfgs['training_data_shape'][-1],
        output_size=len(training_cfgs["to_learn"]),
        num_layers= nn_cfgs.get("num_layers"),
        nodes_per_layer= nn_cfgs.get("nodes_per_layer"),
        activation_funcs= nn_cfgs.get("activation_funcs"),
        biases=nn_cfgs.get("biases"), 
        learning_rate=nn_cfgs.get("learning_rate")
    ).to(device)

    # Initialize the model object
    model = SpeggABM_NN(
        rng=np.random.default_rng(training_cfgs["seed"]),
        h5group=h5group,
        neural_net=net,
        loss_function=training_cfgs["loss_function"],
        epsilon=training_cfgs["epsilon"], 
        to_learn=training_cfgs["to_learn"],
        true_parameters=training_cfgs.get("true_parameters", {}),
        write_every=training_cfgs.get("write_every", 1),
        write_start=training_cfgs.get("write_start", 1),
        training_data=training_data,
        batch_size=training_cfgs.get("batch_size", 4),
        scaling_factors=training_cfgs.get("scaling_factors", {}),
        param_activation_function=training_cfgs.get("activation_function", None)
    )

    # Train the model
    log.info(f"   Now commencing training for {training_cfgs["num_epochs"]} epochs ...")
    for i in range(training_cfgs["num_epochs"]):
        model.epoch()
        log.info(
            f"   Completed epoch {i+1} / {training_cfgs["num_epochs"]}; "
            f"   current loss: {model.current_loss}"
        )
    
    log.info("   Simulation run finished.")
    log.info("   Wrapping up ...")
    h5file.close()

    log.info("   All done.")
    


