#include "FishSim.hpp"

FishSim::FishSim(
    const StringVector&    		parameterNames, 
    const py::array_t<float>& 	demeWideParameters, 
    const StringFloatMap& 		speciesSpecificValues, 
    const StringVector& 		phenotypeNames, 
    const String2DVector& 		genPhenParameterNamesAllPhenotypes, 
    const FloatArrayVector& 	demeSpecificPhenParametersAllPhenotypes, 
    const StringVector& 		lociNames, 
    const py::array_t<float>& 	recombinationRates, 
    const py::array_t<float>&  	demeSpecificMutationRates, 
    const py::array_t<float>&	demeSpecificMutationMagnitudes
) : Simulation() {
    initpop =50*demes;
	maxpop = 1000*demes;

	nspecies = 1;
	
	initialize_classes(
		parameterNames, 
		demeWideParameters, 
		speciesSpecificValues, 
		phenotypeNames, 
		genPhenParameterNamesAllPhenotypes, 
		demeSpecificPhenParametersAllPhenotypes, 
		lociNames, 
		recombinationRates, 
		demeSpecificMutationRates, 
		demeSpecificMutationMagnitudes
	);
}

void FishSim::initialize_classes() {
    std::cout << "Initializing classes for the simulation for the fish evolution model..." << std::endl;
}

void FishSim::initialize_classes(
    const StringVector&    		parameterNames, 
    const py::array_t<float>& 	demeWideParameters, 
    const StringFloatMap& 		speciesSpecificValues, 
    const StringVector& 		phenotypeNames, 
    const String2DVector& 		genPhenParameterNamesAllPhenotypes, 
    const FloatArrayVector& 	demeSpecificPhenParametersAllPhenotypes, 
    const StringVector& 		lociNames, 
    const py::array_t<float>& 	recombinationRates, 
    const py::array_t<float>&  	demeSpecificMutationRates, 
    const py::array_t<float>&	demeSpecificMutationMagnitudes
) {
    array = new inds_stochastic *[nspecies];
	int species_ID = 0;
	array[0] = new Fish(initpop, maxpop, seed, demes, species_ID, 
		parameterNames, 
		demeWideParameters, 
		speciesSpecificValues, 
		phenotypeNames, 
		genPhenParameterNamesAllPhenotypes, 
		demeSpecificPhenParametersAllPhenotypes, 
		lociNames, 
		recombinationRates, 
		demeSpecificMutationRates, 
		demeSpecificMutationMagnitudes
	);

	stats_fish = new FishStatistics(demes);
}

void FishSim::run() {
    std::cout << "Running the simulation for the fish evolution model..." << std::endl;
}

std::vector<std::vector<float>> FishSim::run_return(const bool& run_alone) {
    if (run_alone) {
		array[0]-> exportCsv("initial_data.csv");
	}
	std::vector<std::vector<float>> mean_demes_vec(nsteps, std::vector<float>(demes, 0.0f));

	for (int t = 0 ; t < nsteps ; t++) {
		for (int i = 0 ; i < nspecies ; i++) 
			{
			array[i]->addKids();
			array[i]->update(array);
			array[i]->removeDead();
			}
		
		int genotype_index_of_interest = 0; // assuming we are interested in the first genotype for fecundity

		stats_fish->calculate_mean_genotypes_by_deme(array[0], genotype_index_of_interest);
		// std::cout << "The average genotypes at locus 1 for the two demes are:" << std::endl;
		// stats_fish->print_mean_genotypes_by_deme();
		if (run_alone) {
			array[0]-> exportCsv("final_data.csv");
		}
		// returns the mean phenotypes of all demes
		thrust::device_vector<float> mean_demes = stats_fish->get_mean_fecundity_genotype_by_deme();

		// copy to a regular vector'
		std::vector<float> mean_demes_host(mean_demes.begin(), mean_demes.end());
		mean_demes_vec[t] = mean_demes_host;

		if (run_alone) {
			std::cout << "\rIteration " << (t + 1) << "/" << nsteps << std::flush;
		}
	}

    if (run_alone)
        std::cout << std::endl;

	
	return mean_demes_vec;
}

FishSim::~FishSim() {
    /* cleanup */
	for (int i=0; i < nspecies; i++)
		{
		delete array[i];
		}

	delete[] array;
	delete stats_fish;
}
