from ensemble_training import *

def simulate_population(params : Iterable):
    """
    Docstring for objective_function
    
    :param params: Description
    :type params: np.ndarray
        * 0 - 3: demewide_parameters deme 1
        * 4 - 7: demewide_parameters deme 2
        * 8 - 11: demewide_parameters deme 3
        * 12 - 15: demewide_parameters deme 4
        * 16 - 19: phen1 gene phen map constant
        * 20 - 23: phen 1 gene phen map coef 0
        * 24 - 27: phen 1 gene phen map coef 1
        * 28 - 31: phen 2 gene phen map constant
        * 32 - 35: phen 2 gene phen map coef 0
        * 36 - 39: phen 3 gene phen map constant
        * 40 - 43: phen 3 gene phen map coef 0
        * 44 - 46: loci 1,2,3 recombination rates
        * 47 - 50: loci 1 deme mutation rates
        * 51 - 54: loci 2 deme mutation rates
        * 55 - 58: loci 3 deme mutation rates
        * 59 - 62: loci 1 deme mutation magnitudes
        * 63 - 66: loci 2 deme mutation magnitudes
        * 67 - 70: loci 3 deme mutation magnitudes
    """
    parameter_names = ["M_reproductive_advantage", "F_reproductive_advantage","TARGET_CROWN_COLOR","CROWN_COLOR_DECAY"]

    demewide_parameters = np.array([
        params[:4], params[4:8], params[8:12], params[12:16]
    ], dtype=np.float32)

    # print(demewide_parameters.shape)

    species_specific_values = {
        "FECUNDITY_PHENOTYPE_INDEX"  :  0,
        "MORTALITY_PHENOTYPE_INDEX"  :  1, 
        "CROWN_COLOR_INDEX"          :  2
    }

    phenotype_names = ["FECUNDITY_PHENOTYPE_INDEX", "MORTALITY_PHENOTYPE_INDEX", "CROWN_COLOR_INDEX"]

    genotype_phenotype_parameter_names_all_phenotypes = [
        ["GENPHEN_MAP_CONSTANT", "GENPHEN_MAP_COEF0","GENPHEN_MAP_COEF1"], 
        ["GENPHEN_MAP_CONSTANT", "GENPHEN_MAP_COEF0"], 
        ["GENPHEN_MAP_CONSTANT", "GENPHEN_MAP_COEF0"]
    ]

    deme_specific_phenotype_parameters_all_phenotypes = [
        np.array([params[16:20], params[20:24], params[24:28]], dtype=np.float32), 
        np.array([params[28:32], params[32:36]], dtype=np.float32), 
        np.array([params[36:40], params[40:44]], dtype=np.float32)
    ]

    loci_names = ["locus0", "locus1", "locus2"]

    recombination_rates = np.array(params[44:47], dtype=np.float32)

    deme_specific_mutation_rates = np.array([
        params[47:51], params[51:55], params[55:59]
    ], dtype=np.float32)

    deme_specific_mutation_magnitudes = np.array([
        params[59:63], params[63:67], params[67:]
    ], dtype=np.float32)

    target_phenotypes = [0.5, 0.5, 0.5, 0.5]


    return simulate(
        parameter_names, demewide_parameters, species_specific_values, 
        phenotype_names, genotype_phenotype_parameter_names_all_phenotypes, 
        deme_specific_phenotype_parameters_all_phenotypes, 
        loci_names, recombination_rates, deme_specific_mutation_rates, 
        deme_specific_mutation_magnitudes
    )