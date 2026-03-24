from ensemble_training import *

def simulate_population(params : Iterable):
    """
    Docstring for objective_function
    
    :param params: Description
    :type params: np.ndarray
        * 0 - 3: demewide_parameters deme 1
        * 4: phen1 gene phen map constant
        * 5: phen 1 gene phen map coef 0
        * 6: phen 1 gene phen map coef 1
        * 7: phen 2 gene phen map constant
        * 8: phen 2 gene phen map coef 0
        * 9: phen 3 gene phen map constant
        * 10: phen 3 gene phen map coef 0
        * 11-13: loci 1,2,3 recombination rates
        * 14: loci 1 deme mutation rates
        * 15: loci 2 deme mutation rates
        * 16: loci 3 deme mutation rates
        * 17: loci 1 deme mutation magnitudes
        * 18: loci 2 deme mutation magnitudes
        * 19: loci 3 deme mutation magnitudes
    """
    parameter_names = ["M_reproductive_advantage", "F_reproductive_advantage","TARGET_CROWN_COLOR","CROWN_COLOR_DECAY"]

    demewide_parameters = np.array([
        params[:4]
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
        np.array([params[4:5], params[5:6], params[6:7]], dtype=np.float32), 
        np.array([params[7:8], params[8:9]], dtype=np.float32), 
        np.array([params[9:10], params[10:11]], dtype=np.float32)
    ]

    loci_names = ["locus0", "locus1", "locus2"]

    recombination_rates = np.array(params[11:14], dtype=np.float32)

    deme_specific_mutation_rates = np.array([
        params[14:15], params[15:16], params[16:17]
    ], dtype=np.float32)

    deme_specific_mutation_magnitudes = np.array([
        params[17:18], params[18:19], params[19:20]
    ], dtype=np.float32)


    return simulate(
        parameter_names, demewide_parameters, species_specific_values, 
        phenotype_names, genotype_phenotype_parameter_names_all_phenotypes, 
        deme_specific_phenotype_parameters_all_phenotypes, 
        loci_names, recombination_rates, deme_specific_mutation_rates, 
        deme_specific_mutation_magnitudes
    )