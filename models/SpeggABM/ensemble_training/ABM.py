from ensemble_training import *

class Loss(torch.nn.Module):
    def __init__(self, batch_size, loss_func, epsilon):
        super().__init__()
        self.batch_size = batch_size
        self.loss_func = loss_func
        self.epsilon = epsilon

        self.ABM = ABM()
    
    def forward(self, predicted_parameters, true_records):
        # Problem here is that we are subbing parameter entries that are 0.0 
        # with 1.0, because spegg model can't go with zeros without producing 
        # some NaNs - this design is a hack that guards against this NaNs issue, 
        # but not really mathematically pricipled and should be reconsidered.

        return self.ABM.apply(predicted_parameters, true_records, self.batch_size, self.loss_func, self.epsilon)

class ABM(torch.autograd.Function):

    @staticmethod
    def forward(ctx, predicted_parameters : torch.Tensor, true_records, batch_size, loss_func, epsilon):
        ctx.saved_params = predicted_parameters.detach().numpy()
        ctx.true_records = true_records
        ctx.input_shape = predicted_parameters.shape[-1]
        ctx.batch_size = batch_size
        ctx.loss_func = loss_func
        ctx.epsilon = epsilon

        predicted_parameters = ctx.saved_params.copy()
        predicted_parameters[predicted_parameters < 1e-3] = 1.0

        predicted_pop = simulate_population(predicted_parameters)[:ctx.batch_size]
        return ctx.loss_func(predicted_pop, true_records)

    @staticmethod
    def backward(ctx, grad_output):
        grad_tensor : torch.Tensor = torch.zeros(ctx.input_shape)
        params = ctx.saved_params.copy()
        params[params == 0.0] = 1.0
        for i in range(ctx.input_shape):

            params_up = params.copy()
            params_up[i] += ctx.epsilon

            params_low = params.copy()
            params_low[i] -= ctx.epsilon

            predicted_pop_up = simulate_population(params_up)[:ctx.batch_size]
            predicted_pop_low = simulate_population(params_low)[:ctx.batch_size]

            loss_up = ctx.loss_func(predicted_pop_up, ctx.true_records)
            loss_low = ctx.loss_func(predicted_pop_low, ctx.true_records)

            grad_tensor[i] = ((loss_low - loss_up)) / (2 * ctx.epsilon)
        
        return grad_output * grad_tensor, None, None, None, None
        

    
def simulate_population(params : Iterable) -> torch.Tensor:
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
    ], dtype=np.float32).T

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

    os.chdir(SIMULATION_CONF)

    constructed_pop =  simulate(
        parameter_names, demewide_parameters, species_specific_values, 
        phenotype_names, genotype_phenotype_parameter_names_all_phenotypes, 
        deme_specific_phenotype_parameters_all_phenotypes, 
        loci_names, recombination_rates, deme_specific_mutation_rates, 
        deme_specific_mutation_magnitudes, False
    )

    os.chdir(os.path.dirname(__file__))

    return torch.tensor(constructed_pop, dtype=torch.float32)