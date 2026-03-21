#ifndef PENGUIN_SIMULATOR_H
#define PENGUIN_SIMULATOR_H

#include <Simulation_Class.h>
#include "Penguins.h"
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

class PenguinStatistics : public Statistics {
	public:
		PenguinStatistics(int demes) : Statistics(demes) {}

		thrust::device_vector<float> get_mean_phenotypes_by_deme() {
			return mean_genotypes;
		}
};

class Penguin_Drift_Simulator : public Simulation
	{
	public:
		Penguin_Drift_Simulator();

		Penguin_Drift_Simulator(
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

		~Penguin_Drift_Simulator();

		void run();
		
		std::vector<std::vector<float>> run_return();
	private:
		inds_stochastic **array;
		PenguinStatistics *stats_penguins;
		void initialize_classes();

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

		int nspecies;
	};
#endif
