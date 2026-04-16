#include "FishParents.hpp"
#include "Fish.hpp"

FishParents::FishParents(Fish *species) : Parents(species) {
    FECUNDITY_PHENOTYPE_INDEX = demeParameters->species_specific_values["FECUNDITY_PHENOTYPE_INDEX"];
}

void FishParents::determine_probability_individual_becomes_male_parent() {
    thrust::multiplies<float> op;
	thrust::transform(
        will_reproduceM.begin(), 
        will_reproduceM.begin() + size, 
        phenotype[FECUNDITY_PHENOTYPE_INDEX].begin(),  
        probability_individual_becomes_male_parent.begin(), 
        op
    );
}

void FishParents::determine_probability_individual_becomes_female_parent() {
    thrust::multiplies<float> op;
    thrust::transform(
        will_reproduceF.begin(), 
        will_reproduceF.begin() + size, 
        phenotype[FECUNDITY_PHENOTYPE_INDEX].begin(),  
        probability_individual_becomes_female_parent.begin(), 
        op
    );
}
