from ruamel.yaml import YAML
from ensemble_training import *

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
    cfgs = load_config("SPEGG_cfg.yml")
    # Get the Training config, initialize training data generation
    data_gen_cfgs = cfgs['Data']
    # Generate training data
    training_data = generate_training_data(
        data_gen_cfgs, 
        process_output(out.stdout, delimiter=data_gen_cfgs['delimiter'])
    )

    print(training_data)
