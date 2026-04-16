#ifndef FISH_HPP
#define FISH_HPP

#include <species/inds_stochastic.h>

#include "FishParents.hpp"
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

/**
 * @brief Models the static states of fish population, such as their genotypes, phenotypes, 
 * and sexes. This state will change across simulation time steps.
 * 
 */
class Fish : public inds_stochastic {

    public:
        
        /**
         * @brief Construct a new Fish object
         * 
         * @param size_val starting size of the population of the fish species
         * @param maxsize_val the maximal capacity that can hold individuals of the fish species
         * @param seed_val seed value for the random generator
         * @param ndemes number of demes into which individuals of the fish species are split
         * @param species_ID_val ID value for the fish species, preferably 0
         * @param parameterNames vector of parameter names
         * @param demeWideParameters array of deme-wide parameters
         * @param speciesSpecificValues map of species-specific values
         * @param phenotypeNames vector of phenotype names
         * @param genPhenParameterNamesAllPhenotypes 2D vector of genotype-phenotype parameter names for all phenotypes
         * @param demeSpecificPhenParametersAllPhenotypes vector of arrays of deme-specific phenotype parameters for all phenotypes
         * @param lociNames vector of locus names
         * @param recombinationRates array of recombination rates
         * @param demeSpecificMutationRates array of deme-specific mutation rates
         * @param demeSpecificMutationMagnitudes array of deme-specific mutation magnitudes
         */
        Fish(
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
        
        /**
         * @brief Adds new individuals to the fish population
         * 
         */
        void addKids();

        using inds_stochastic::update;
        /**
         * @brief Updates the state of the fish population
         * 
         * @param species array of pointers to all species. But we only have one species here, 
         * so the structure should be [ [ Fish ] ]
         */
        void update(inds_stochastic **species);

    protected:
        /**
         * @brief Initializes the demes of the fish population
         * 
         */
        void initialize_demes();
        /**
         * @brief Sets the phenotype of an individual fish
         * 
         * @param index index of the individual fish
         * @param n deme index of the individual fish
         */
        void setPhenotype(int index, int n);

        /**
         * @brief Assigns the sex of an individual fish
         * 
         * @param index index of the individual fish
         * @param n deme index of the individual fish
         */
        void assignSex(int index, int n);
};


#endif