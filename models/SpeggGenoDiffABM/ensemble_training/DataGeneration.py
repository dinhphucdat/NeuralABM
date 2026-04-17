from ensemble_training import *

READS_PATH = os.path.join(
    os.path.dirname(__file__), 
    "read_simulator"
)

def generate_training_data():
    """
    Generates allele frequency data from DNA sequencing - implement later
    """
    pass

def run_sequencing_snparcher():
    """
    Runs with snpArcher
    """
    tsteps = [d for d in os.listdir(READS_PATH) if os.path.isdir(d)]

    for t in tsteps:
        # Define absolute path for data to avoid 'cd' confusion
        data_dir = os.path.abspath(os.path.join("read_simulator", t))
        snparcher_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "snpArcher"))
        SHELL = f"""
            # Create snparcher environment
            if [[ ! $(conda env list | grep snparcher) ]]; then
                mamba create -c conda-forge -c bioconda -n snparcher "snakemake>=9" "python==3.11.4"
            fi

            # Hook mamba into the shell
            eval "$(mamba shell hook --shell bash)"

            # Activate the snparcher environment
            mamba activate snparcher

            # Go to snpArcher
            cd {snparcher_dir}

            # Run snparcher pipeline
            snakemake -d {data_dir} --cores 1 --use-conda --workflow-profile workflow-profiles/default

            # Genetic info extracting
            vcftools --gzvcf {os.path.join(data_dir, 'results/vcfs/raw.vcf.gz')} --freq2 --stdout

        """
        os.system(SHELL)
