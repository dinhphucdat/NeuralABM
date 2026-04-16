#include "FishSim.hpp"

#include <sstream>
#include <fstream>
#include <iostream>
#include <stdio.h>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/embed.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <pybind11/complex.h>
#include <util/python_thrust_api.h>

namespace py = pybind11;
using StringVector = std::vector<std::string>;
using String2DVector = std::vector<std::vector<std::string>>;
using StringFloatMap = std::map<std::string, float>;
using FloatArrayVector = std::vector<py::array_t<float>>;

int main() {
    std::cout << "Please use the Python wrapper to run the simulation" << std::endl;
    return 0;
}

std::vector<std::vector<float>> simulate(
    const StringVector&    		parameterNames, 
	const py::array_t<float>& 	demeWideParameters, 
	const StringFloatMap& 		speciesSpecificValues, 
	const StringVector& 		phenotypeNames, 
	const String2DVector& 		genPhenParameterNamesAllPhenotypes, 
	const FloatArrayVector& 	demeSpecificPhenParametersAllPhenotypes, 
	const StringVector& 		lociNames, 
	const py::array_t<float>& 	recombinationRates, 
	const py::array_t<float>&  	demeSpecificMutationRates, 
	const py::array_t<float>&	demeSpecificMutationMagnitudes, 
	const bool&					run_alone
) {
    FishSim fish_sim(
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
    return fish_sim.run_return(run_alone);
}

PYBIND11_MODULE(GenotypeDiffFecundity, m) {
    m.doc() = "Fish simulation wrapper in Python";
    m.def("simulate", &simulate, "Run the fish simulation and return the mean phenotypes by deme");
}
