#include "Penguin_Drift_Simulator.h"

Penguin_Drift_Simulator::Penguin_Drift_Simulator() : Simulation()
	{
	initpop =50*demes;
	maxpop = 1000*demes;

	nspecies = 1;
	
	initialize_classes();
	}

Penguin_Drift_Simulator::Penguin_Drift_Simulator(
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
) : Simulation()
	{
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

void Penguin_Drift_Simulator::initialize_classes()
	{
	array = new inds_stochastic *[nspecies];
	int species_ID = 0;
	array[0] = new Penguins(initpop, maxpop, seed, demes, species_ID);

	stats_penguins = new PenguinStatistics(demes);

	array[0]-> exportCsv("initial_data.csv");
	}

void Penguin_Drift_Simulator::initialize_classes(
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
)
	{
	array = new inds_stochastic *[nspecies];
	int species_ID = 0;
	array[0] = new Penguins(initpop, maxpop, seed, demes, species_ID, 
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

	stats_penguins = new PenguinStatistics(demes);
	}

void Penguin_Drift_Simulator::run() {}


std::vector<std::vector<float>> Penguin_Drift_Simulator::run_return(const bool& run_alone)
	{
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
		
		int genotype_index_of_interest = 2;

		stats_penguins->calculate_mean_genotypes_by_deme(array[0], genotype_index_of_interest);
		// std::cout << "The average genotypes at locus 1 for the two demes are:" << std::endl;
		// stats_penguins->print_mean_genotypes_by_deme();
		if (run_alone) {
			array[0]-> exportCsv("final_data.csv");
		}
		// returns the mean phenotypes of all demes
		thrust::device_vector<float> mean_demes = stats_penguins->get_mean_phenotypes_by_deme();

		// copy to a regular vector'
		std::vector<float> mean_demes_host(mean_demes.begin(), mean_demes.end());
		mean_demes_vec[t] = mean_demes_host;

		if (run_alone) {
			std::cout << "\rIteration " << (t + 1) << "/" << nsteps << std::flush;
			std::cout << std::endl;
		}
	}

	
	return mean_demes_vec;
	}


Penguin_Drift_Simulator::~Penguin_Drift_Simulator()
	{
	/* cleanup */
	for (int i=0; i < nspecies; i++)
		{
		delete array[i];
		}

	delete[] array;
	delete stats_penguins;
	}
