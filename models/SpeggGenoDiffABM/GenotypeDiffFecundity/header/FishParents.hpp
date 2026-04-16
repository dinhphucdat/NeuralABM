#ifndef FISH_PARENTS_HPP
#define FISH_PARENTS_HPP

#include <species/add_kids/parents_class.h>

/**
 * @brief Models the parents of the fish species, including their reproductive eligibility 
 * and probabilities.
 * 
 */
class FishParents : public Parents {

    /// @brief pointer to the fish species instance that this class is associated with
    class Fish *species;

	public:
        /**
         * @brief Construct a new Fish Parents object
         * 
         * @param species the pointer to the fish species instance that this class is associated with
         */
		FishParents(Fish *species);
		
	protected:
        /// @brief index of the phenotype that determines the fecundity of the fish individuals
		int FECUNDITY_PHENOTYPE_INDEX;
        /**
         * @brief Determines the probability that each individual becomes a female parent based on their fecundity phenotype.
         * This function overrides the virtual function in the base class `Parents` and implements the logic specific to the fish species.
         */
		void determine_probability_individual_becomes_female_parent();
        /**
         * @brief Determines the probability that each individual becomes a male parent based on their fecundity phenotype.
         * This function overrides the virtual function in the base class `Parents` and implements the logic specific to the fish species.
         */
		void determine_probability_individual_becomes_male_parent();

};

#endif