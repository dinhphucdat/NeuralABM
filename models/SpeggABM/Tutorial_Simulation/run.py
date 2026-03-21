#!/home/wormlab/miniforge3/bin/python

import Tutorial_Simulation
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error as mse
from scipy.optimize import minimize

def objective_function(params : np.ndarray, loss=False):
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


    actual_phenotypes = Tutorial_Simulation.simulate(
        parameter_names, demewide_parameters, species_specific_values, 
        phenotype_names, genotype_phenotype_parameter_names_all_phenotypes, 
        deme_specific_phenotype_parameters_all_phenotypes, 
        loci_names, recombination_rates, deme_specific_mutation_rates, 
        deme_specific_mutation_magnitudes
    )

    return mse(np.sum(np.array(target_phenotypes), axis=0) ** 3, np.array(actual_phenotypes) ** 3) if loss else actual_phenotypes


def iterate():
    parameter_names = ["M_reproductive_advantage", "F_reproductive_advantage","TARGET_CROWN_COLOR","CROWN_COLOR_DECAY"]

    demewide_parameters = np.array([
        np.random.rand(4) for _ in range(4)
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
        np.array(arr, dtype=np.float32) 
        for arr in [
            [np.random.uniform(0.01, 3, 4) for _ in range(3)], 
            [np.random.uniform(0.01, 3, 4) for _ in range(2)],
            [np.random.uniform(0.01, 3, 4) for _ in range(2)]
        ]
    ]

    loci_names = ["locus0", "locus1", "locus2"]

    recombination_rates = np.array(np.random.rand(3), dtype=np.float32)

    deme_specific_mutation_rates = np.array([
        np.random.uniform(0.01, 10, 4) for _ in range(3)
    ], dtype=np.float32)

    deme_specific_mutation_magnitudes = np.array([
        np.random.rand(4) for _ in range(3)
    ], dtype=np.float32)


    return Tutorial_Simulation.simulate(
        parameter_names, demewide_parameters, species_specific_values, 
        phenotype_names, genotype_phenotype_parameter_names_all_phenotypes, 
        deme_specific_phenotype_parameters_all_phenotypes, 
        loci_names, recombination_rates, deme_specific_mutation_rates, 
        deme_specific_mutation_magnitudes
    )

def plot_average_phenotypes():
    size = 30
    res_1 = np.zeros(size)
    res_2 = np.zeros(size)
    res_3 = np.zeros(size)
    res_4 = np.zeros(size)

    for i in range(size):
        sim_result = iterate()
        res_1[i] = sim_result[0]
        res_2[i] = sim_result[1]
        res_3[i] = sim_result[2]
        res_4[i] = sim_result[3]

    fig, ax = plt.subplots(2,2)
    ax[0,0].plot(range(size), res_1)
    ax[0,0].set_title("Deme 1 avg phen")
    ax[0,1].plot(range(size), res_2)
    ax[0,1].set_title("Deme 2 avg phen")
    ax[1,0].plot(range(size), res_3)
    ax[1,0].set_title("Deme 3 avg phen")
    ax[1,1].plot(range(size), res_4)
    ax[1,1].set_title("Deme 4 avg phen")
    fig.savefig("plot.png")

def plot_phenotype_correlation(deme1 : int, deme2 : int):
    size = 30
    res_1 = np.zeros(size)
    res_2 = np.zeros(size)
    res_3 = np.zeros(size)
    res_4 = np.zeros(size)

    for i in range(size):
        sim_result = iterate()
        res_1[i] = sim_result[0]
        res_2[i] = sim_result[1]
        res_3[i] = sim_result[2]
        res_4[i] = sim_result[3]
    
    def determine_deme(deme : int):
        match deme:
            case 1:
                return res_1
            case 2:
                return res_2
            case 3:
                return res_3
            case _:
                return res_4
    
    res_d1 = determine_deme(deme1)
    res_d2 = determine_deme(deme2)
    
    plt.scatter(res_d1, res_d2)
    plt.xlabel("Deme 1 avg phen")
    plt.ylabel("Deme 2 avg phen")
    plt.savefig(f"plot_phen_corr_deme_{deme1}_{deme2}.png")
    plt.close()

"""
plot_phenotype_correlation(1,2)
plot_phenotype_correlation(2,3)
plot_phenotype_correlation(3,4)
plot_phenotype_correlation(1,3)
plot_phenotype_correlation(1,4)
plot_phenotype_correlation(2,4)
"""

"""
optim = minimize(objective_function, np.random.uniform(0.1, 20, 71), args=(True,), method='BFGS')
print(optim.x)
print("The optimal demewise mean phenotypes:", objective_function(optim.x))
print("The optimal loss:", objective_function(optim.x, loss=True))
"""

def collect_values():
    v = objective_function(
        [11.76212958, 10.94996127, 10.16830509,  8.39087327, 10.60904357,  1.44443913,
    16.16616173, 15.873428  ,  4.84957699 , 3.39787509 ,10.7776903 , 11.73729405,
    7.2609076 ,  7.67055232 , 7.71990415 , 7.23063468 ,16.62130382 ,16.77443802,
    8.3975074 ,  7.53496507,  1.70042552, 3.51298666 , 3.97492131 , 3.4387258,
    18.0562934  , 2.53255635 , 4.64927706 ,11.97032706 ,17.35218506 , 8.87133259,
    9.8223982 ,  6.74866343 , 9.19822732,  8.80980767 , 0.90249064 ,13.02810947,
    8.428498  ,  3.34903409 , 0.79688786 , 7.21275838, 14.92076762, 10.53417573,
    9.39068632 , 9.72960571 ,12.75708773 , 5.6162265 , 10.79666626 , 8.05223031,
    16.56532202 , 1.01025239 , 9.65956205 , 0.24609081 ,11.86165985, 12.49446631,
    14.9260639 , 10.00447759 , 9.0269841 , 18.64207265, 13.54081168 , 8.05352636,
    0.70519754 , 5.60590258 , 0.7410638  , 8.19085421 , 6.3212924  ,13.92941139,
    6.9798819 , 16.85305258 ,14.18784038,  6.13239034,  7.53766189]
    )
    print(f"{'t_step':<10}{'deme1':<10}{'deme2':<10}{'deme3':<10}{'deme4':<10}")
    for i, x in enumerate(v):
        print(f"{i:<10}{x[0]:<10.4f}{x[1]:<10.4f}{x[2]:<10.4f}{x[3]:<10.4f}")
        
collect_values()
