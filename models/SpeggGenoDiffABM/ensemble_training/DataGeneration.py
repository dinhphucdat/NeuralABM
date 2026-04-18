#!/home/wormlab/miniforge3/bin/python3
from ensemble_training import *
import subprocess

READS_PATH = os.path.join(
    os.path.dirname(__file__), 
    "read_simulator"
)

def generate_training_data(data_cfgs : dict) -> torch.Tensor:
    """
    Generates allele frequency data from DNA sequencing - implement later
    """
    return torch.tensor(run_sequencing_snparcher(data_cfgs), dtype=torch.float32)

def process_freq_result(output : str):
    matrix = []
    lines = output.strip().split("\n")
    lines = lines[1:] # Drop the header
    for line in lines:
        matrix.append([(float(n) if is_float(n) else n) for n in line.split("\t")])
    return matrix

def is_float(n):
    try:
        float(n)
        return True
    except:
        return False

def run_sequencing_snparcher(data_cfgs : dict):
    """
    Runs with snpArcher
    """
    tsteps = [d for d in os.listdir(READS_PATH) if os.path.isdir(os.path.join(READS_PATH, d))]

    training_data = []

    for t in tsteps:
        # Define absolute path for data to avoid 'cd' confusion
        data_dir = os.path.abspath(os.path.join(READS_PATH, t))
        snparcher_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "snpArcher"))
        
        subprocess.run([f'{os.path.dirname(__file__)}/setup_spegg.sh', snparcher_dir, data_dir], text=True)

        genetic_t = subprocess.run(
            [
                'mamba', 
                'run', '-n', 'snparcher',
                'vcftools', 
                '--gzvcf', 
                os.path.join(data_dir, "results/vcfs/raw.vcf.gz"), 
                '--freq2', 
                '--stdout'], 
            capture_output=True, text=True
        )

        training_data.append(
            parse_genetic_output(
                genetic_t.stdout,
                nloci=data_cfgs['nloci'],
                pos_loci_interst=data_cfgs['pos_loci_interest'],
                pos_col_allele_interest=data_cfgs['pos_col_allele_interest'], 
                output_sep=data_cfgs.get('output_sep', "\t")
            )
        )
    return training_data

def parse_genetic_output(genetic_output : str, nloci : int, pos_loci_interst : int, pos_col_allele_interest : int, output_sep = "\t") -> list:
    """
    Parses out the genetic output from the vcftools into a population matrix. 
    This function is called after each timestep of the simulation

    :param genetic_output: The output from the vcftools command
    :param nloci: The number of loci in the simulation
    :param pos_loci_interst: The column position of the loci of interest in the output. 
        This is used to ensure that we are parsing the correct loci from the output.
    :param pos_col_allele_interest: The column position of the allele of interest in the output. 
    :param output_sep: The separator used in the output from the vcftools (default is tab)
    :return: A list of lists representing the population matrix
    :rtype: list
    """
    matrix = []
    lines = genetic_output.strip().split("\n")
    header = lines[0]
    data = lines[1:]
    for line in data:
        parts = line.split(output_sep)
        if len(parts) > pos_col_allele_interest:
            matrix.append(
                float(parts[pos_col_allele_interest]) 
                    if is_float(parts[pos_col_allele_interest]) 
                    else parts[pos_col_allele_interest]
            )
        else:
            matrix.append(0.0) # If the allele of interest is not present, we can assume its frequency is 0.0 
            # (i.e. the allele is not present)
    if len(matrix) < nloci:
        # If there are fewer loci in the output than expected, we can pad the matrix with 1.0s
        matrix.extend([1.0] * (nloci - len(matrix)))
    return matrix[pos_loci_interst:pos_loci_interst+1] # Return only the loci of interest (should be a list of length 1)

if __name__ == "__main__":
    print(generate_training_data({
        'nloci': 3,
        'pos_loci_interest': 0,
        'pos_col_allele_interest': 5,
        'output_sep': "\t"
    }))
