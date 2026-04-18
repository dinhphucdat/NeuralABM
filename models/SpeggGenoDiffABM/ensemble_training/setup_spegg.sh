#!/usr/bin/bash

RUN_SNPARCHER() {
    # $1: snparcher_dir
    # $2: data_dir
    # Create snparcher environment
    if [[ ! $(conda env list | grep snparcher) ]]; then
        mamba create -c conda-forge -c bioconda -n snparcher "snakemake>=9" "python==3.11.4"
    fi

    # Hook mamba into the shell
    eval "$(mamba shell hook --shell bash)"

    # Activate the snparcher environment
    mamba activate snparcher

    # Go to snpArcher
    cd $1

    # Run snparcher pipeline
    snakemake -d $2 --cores 1 --use-conda --workflow-profile workflow-profiles/default
}

RUN_SNPARCHER $1 $2
