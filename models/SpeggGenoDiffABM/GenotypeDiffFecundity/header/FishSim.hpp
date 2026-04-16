#ifndef FISH_SIM_HPP
#define FISH_SIM_HPP

#include <Simulation_Class.h>
#include "Fish.hpp"
#include <math/statistics_class.h>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/embed.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <pybind11/complex.h>
#include <util/python_thrust_api.h>
#include <thrust/device_vector.h>

namespace py = pybind11;
using StringVector = std::vector<std::string>;
using String2DVector = std::vector<std::vector<std::string>>;
using StringFloatMap = std::map<std::string, float>;
using FloatArrayVector = std::vector<py::array_t<float>>;

/**
 * @brief Specifies the statistics object to also be able to 
 * calculate the mean phenotypes across all time steps and demes
 * 
 */
class FishStatistics : public Statistics {
	public:
		FishStatistics(int demes) : Statistics(demes) {}

		thrust::device_vector<float> get_mean_fecundity_genotype_by_deme() {
			return mean_genotypes;
		}
};

/**
 * @brief Simulates the fish evolutionary dynamics
 * 
 */
class FishSim : public Simulation
	{
	public:
		FishSim(
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
		);

		~FishSim();

		void run();
		
		/**
		 * @brief Run the simulation and return the mean phenotypes by deme 
		 * at each time step as a 2D vector. The outer vector has the size of 
		 * number of time steps, and the inner vector has the size of number 
		 * of demes, with each element being the mean phenotype value for that 
		 * deme at that time step.
		 * 
		 * @param run_alone if true, it will also generates csv files of simulated population record and print out the simulation progress
		 * @return std::vector<std::vector<float>> 
		 */
		std::vector<std::vector<float>> run_return(const bool& run_alone = true);
	private:
        /// @brief 2D array of pointers to the fish species instances, with dimensions [number of species][number of demes]
		inds_stochastic **array;
        /// @brief pointer to the statistics object for the fish simulation, which will be used to calculate and store the mean phenotypes by deme across time steps
		FishStatistics *stats_fish;
        /**
         * @brief Initialize the classes used in the fish simulation, including the fish 
         * species instances and the statistics object. This function will be called by 
         * the constructors to set up the necessary resources for the simulation.
         * 
         */
		void initialize_classes();

        /**
         * @brief Initialize the classes used in the fish simulation with the provided parameters, 
         * including the fish species instances and the statistics object.
         * 
         * @param parameterNames parameter names for the fish simulation
         * @param demeWideParameters deme-wide parameters for the fish simulation, stored as a numpy array
         * @param speciesSpecificValues species-specific values for the fish simulation, stored as a map from string to float
         * @param phenotypeNames phenotype names for the fish simulation
         * @param genPhenParameterNamesAllPhenotypes genotype-phenotype parameter names for all phenotypes in the fish simulation, stored as a 2D vector of strings
         * @param demeSpecificPhenParametersAllPhenotypes deme-specific phenotype parameters for all phenotypes in the fish simulation, stored as a vector of numpy arrays
         * @param lociNames loci names for the fish simulation
         * @param recombinationRates recombination rates for the fish simulation, stored as a numpy array
         * @param demeSpecificMutationRates deme-specific mutation rates for the fish simulation, stored as a numpy array
         * @param demeSpecificMutationMagnitudes deme-specific mutation magnitudes for the fish simulation, stored as a numpy array
         */
		void initialize_classes(
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
		);

		/// @brief number of species in the simulation, which is 1 for the fish simulation
		int nspecies;
	};

#endif // FISH_SIM_HPP