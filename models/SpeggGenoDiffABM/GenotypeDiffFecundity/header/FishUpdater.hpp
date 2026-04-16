#ifndef FISH_UPDATER_HPP
#define FISH_UPDATER_HPP

#include <species/update/updatebehavior.h>
#include <util/amplify.h>

#include <thrust/device_vector.h>
#include <thrust/sequence.h>
#include <thrust/transform.h>

/**
 * @brief Update behavior for the fish species, including how to update 
 * their phenotypes and determine their mortality based on their phenotypes.
 * 
 */
class FishUpdater : public UpdateBehavior {
    /// @brief pointer to the fish species instance that this class is associated with
    class inds_stochastic *species;
	// Constructor
	public:
        /**
         * @brief Construct a new Fish Updater object 
         * 
         * @param species pointer to the fish species instance that this class is associated with
         */
        FishUpdater(inds_stochastic *species) {

            this->species = species;
    
            // Copy the constants 
            this->size = species->size;
            this->Number_of_Demes = species->Num_Demes;
        }
        /**
         * @brief Update the fish species
         * 
         */
        void update();

	protected:
        /**
         * @brief Update the fin color phenotype of the fish species based on their 
         * current phenotypic values and the target fin color for their deme. This function 
         * implements the logic specific to how the fin color phenotype should be 
         * updated for the fish species.
         */
		void updateFinColor();

        // variable names
        int MORTALITY_PHENOTYPE_INDEX;
        int FIN_COLOR_INDEX;
        int size;
        int Number_of_Demes;
        void survive();
};

struct fin_color_updater {
	float *fin_phenotypes;
	float *target_fin_color;

	fin_color_updater(float* fin_phens, float* targ_fin_color) : fin_phenotypes(fin_phens), target_fin_color(targ_fin_color)
	{};

	/* 
	Elements in the tuple.
	---------------------
	0: individual's index
	1: individual's deme
	2: the rate at which fin color decays for the individual's deme.
	*/ 

	template <typename tuple>
	__host__ __device__
	void operator()(tuple t) 
		{
		int ind_index = thrust::get<0>(t);
		int ind_deme = thrust::get<1>(t);
		float delta_fin_color = thrust::get<2>(t);

		float old_fin_color = fin_phenotypes[ind_index];
		fin_phenotypes[ind_index] = old_fin_color - delta_fin_color*(old_fin_color - target_fin_color[ind_deme]);
		}   
	};

#endif // FISH_UPDATER_HPP