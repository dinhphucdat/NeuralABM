#include "Fish.hpp"

#include <species/add_kids/genotype_phenotype_map.h>
#include <species/update/updatebehavior.h>

#include <thrust/copy.h>
#include <thrust/fill.h>

Fish::Fish(
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
) : inds_stochastic(
    size_val, maxsize_val, seed_val, ndemes, species_ID_val, 
    parameterNames, demeWideParameters, speciesSpecificValues, 
    phenotypeNames, genPhenParameterNamesAllPhenotypes, 
    demeSpecificPhenParametersAllPhenotypes, lociNames, 
    recombinationRates, demeSpecificMutationRates, 
    demeSpecificMutationMagnitudes
) {
    // Assume everyone starts at age = 0.
	thrust::fill(age.begin(), age.begin() + size, 0);

	initialize_demes();
	
	// Specify the genetics by assuming allelic values are gaussian-distributed
	for (int i=0; i < nloci; i++)
		{		
		draw_gaussian(size, 0, 0.1, fgenotype[i], gen);
		draw_gaussian(size, 0, 0.1, mgenotype[i], gen);
		}

	//Set phenotype
	setPhenotype(0, size);

	// To start, assign odd numbered individuals to be male, even numbered individuals to be female
	thrust::device_vector<int> twos(size);
	thrust::fill(twos.begin(), twos.end(), 2);
	thrust::transform(id.begin(), id.begin() + size, twos.begin(), sex.begin(), thrust::modulus<int>());
}

void Fish::addKids() {
    demeCalculations();

	FishParents *fishParents;
	fishParents = new FishParents(this);
	fishParents->setup_parents();

	if (fishParents->Potential_Number_of_Kids > 0)
		{
		EggsNeonates *fishNeonates;

		fishNeonates = new EggsNeonates (this, fishParents->kids_per_mom);

		fishNeonates->inherit_genotypes(
            fishParents->probability_individual_becomes_female_parent, 
            fishParents->probability_individual_becomes_male_parent
        );

		setPhenotype(fishNeonates->previous_pop_size, fishNeonates->Total_Number_of_Neonates);
		assignSex(fishNeonates->previous_pop_size, fishNeonates->Total_Number_of_Neonates);
		sortByDeme();
		delete fishNeonates;     
		}
	demeCalculations();
	delete fishParents;
}

void Fish::setPhenotype(int index, int num_inds_to_calculate) {
    for (int i=0; i < nphen; i++) {	
		GenotypePhenotypeMap *genotype_phenotype_map;
		genotype_phenotype_map = genotype_phenotype_map->create_genotype_phenotype_map(this, i, index, num_inds_to_calculate);
		genotype_phenotype_map->calculate_phenotype(this);
		delete genotype_phenotype_map;
	}
}

void Fish::update(inds_stochastic **species) {
    UpdateBehavior *updatebehavior;
	updatebehavior = updatebehavior->create_updateBehavior(species, NULL, 0);
	updatebehavior->update();
}

void Fish::initialize_demes() {
    thrust::fill(max_deme_sizes.begin(), max_deme_sizes.begin() + Num_Demes, maxsize/Num_Demes);

	for (int i=0; i < Num_Demes; i++) {
		float startsize = (float) (size/Num_Demes);
		int temp1 = (int) startsize * i;
		int temp2 = (int) startsize * (i+1);
		thrust::fill(deme.begin() + temp1, deme.begin() + temp2, i);
	}
}

void Fish::assignSex(int index, int num_inds_to_calculate) {
	thrust::device_vector<int> neonates_sex(num_inds_to_calculate);
	draw_bernoulli(num_inds_to_calculate, 0.5, neonates_sex, gen);
	thrust::copy(neonates_sex.begin(), neonates_sex.begin() + num_inds_to_calculate, sex.begin() + index);
}
