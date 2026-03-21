#ifndef PENGUINS_H
#define PENGUINS_H

#include <species/inds_stochastic.h>

#include "Penguin_Parents.h"
#include <species/add_kids/neonates_class.h>

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

class Penguins : public inds_stochastic
	{
	public:
		Penguins(int size_val, int maxsize_val, int seed_val, int ndemes, int species_ID_val);

		Penguins(
			int size_val, 
			int maxsize_val, 
			int seed_val, 
			int ndemes, 
			int species_ID_val, 
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

		void addKids();

		using inds_stochastic::update;
		void update(inds_stochastic **species);

	protected:
		void initialize_demes();
		void setPhenotype(int index, int n);
		void assignSex(int index, int n);
	};
#endif
