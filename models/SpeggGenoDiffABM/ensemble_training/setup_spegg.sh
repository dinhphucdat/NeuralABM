#!/usr/bin/bash

# Create snparcher environment
if [[ ! $(conda env list | grep snparcher) ]]; then
    mamba create -c conda-forge -c bioconda -n snparcher "snakemake>=9" "python==3.11.4"
fi

# Hook mamba into the shell
eval "$(mamba shell hook --shell bash)"

# Activate the snparcher environment
mamba activate snparcher

# Go to snpArcher
cd snpArcher

# Run snparcher pipeline
snakemake -d .test/ecoli --cores 1 --use-conda --workflow-profile workflow-profiles/default

# Print allele frequencies
vcftools --gzvcf .test/ecoli/results/vcfs/raw.vcf.gz --freq2 --stdout