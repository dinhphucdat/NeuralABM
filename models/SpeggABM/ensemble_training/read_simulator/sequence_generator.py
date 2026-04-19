#!/home/wormlab/miniforge3/bin/python3

import os, sys
import numpy as np
import pandas as pd
from pathlib import Path

def create_mutation_map(alleles_at_loci : list[str]) -> list[str]:
    """
    Determine how the alleles mutate, which will be used universally throughout
    """
    map = []

    SCHEMES = np.array(['SUB', 'ADD', 'DEL'])
    POSSIBLE_BASES = np.array(['A', 'T', 'G', 'C'])

    for i, locus in enumerate(alleles_at_loci):
        scheme = np.random.choice(SCHEMES)
        if scheme == 'SUB':
            next_base = locus
            while next_base == locus:
                next_base = str(np.random.choice(POSSIBLE_BASES))
            map.append(next_base)
        if scheme == 'ADD': # Assume that we add one nucleotide
            map.append(
                locus + str(np.random.choice(POSSIBLE_BASES))
            )
        if scheme == 'DEL':
            map.append('')
    
    return map

def get_reference_genome_list(filename):
    """
    Parse the fasta file into a list of a base per element
    """
    with open(filename, 'r') as f:
        every = f.readlines()
        first_line = every[0]
        bp = [* ''.join(every[1:])]
    return bp, first_line

MUTATION_LOCATIONS = [10, 50, 100]
REF_GENOME_ARR, FIRST_LINE = get_reference_genome_list('local_genome.fasta')
MUTATION_MAP = create_mutation_map(REF_GENOME_ARR)

def generate_sequence_one_individual():
    """
    Determine if 
    Reference genome should be a lis
    """
    has_mutation_locus_0 = np.random.choice(np.array([True, False]))
    has_mutation_locus_1 = np.random.choice(np.array([True, False]))
    has_mutation_locus_2 = np.random.choice(np.array([True, False]))

    new_seq = []

    for i, bp in enumerate(REF_GENOME_ARR):
        if i == MUTATION_LOCATIONS[0] and has_mutation_locus_0:
            new_seq.append(MUTATION_MAP[0])
        elif i == MUTATION_LOCATIONS[1] and has_mutation_locus_1:
            new_seq.append(MUTATION_MAP[1])
        elif i == MUTATION_LOCATIONS[2] and has_mutation_locus_2:
            new_seq.append(MUTATION_MAP[2])
        else:
            new_seq.append(bp)
    
    return ''.join(new_seq)

def generate_time_series_sequences(n_inds : int, n_timesteps : int):
    """
    Create reads
    """
    BASE_DIR = os.path.dirname(__file__)
    for i in range(n_timesteps):
        CURRENT_TSTEP = os.path.join(BASE_DIR, f't_{i}')
        if not os.path.exists(CURRENT_TSTEP):
            os.mkdir(CURRENT_TSTEP)
        if not os.path.exists(os.path.join(CURRENT_TSTEP, "data")):
            os.mkdir(os.path.join(CURRENT_TSTEP, "data"))
        for j in range(n_inds):
            CURRENT_IND = os.path.join(os.path.join(CURRENT_TSTEP, "data"), f'ind_{j}')
            if not os.path.exists(CURRENT_IND):
                os.mkdir(CURRENT_IND)
            current_inds_sequence = generate_sequence_one_individual()
            with open(os.path.join(CURRENT_IND, 'seq.fasta'), 'w') as f:
                f.write(FIRST_LINE + '\n' + current_inds_sequence)
            print(f'Generate sequence for individual {j} at time step {i}')
            os.system(f'art_454 -B {os.path.join(CURRENT_IND, 'seq.fasta')} {os.path.join(CURRENT_IND, 'seq')} {50} > /dev/null')
            os.system(f'sed -i \'s/-[12]$//\' {os.path.join(CURRENT_IND, '*.fq')}')
        
        generate_config_and_samsheet(CURRENT_TSTEP, os.path.join(BASE_DIR, "local_genome.fasta"))

def generate_config_and_samsheet(timestep_dir, path_to_reference_file):
    """
    If there is not yet any .fq file and .fasta reference, this will throw and error
    """
    if not os.path.exists(os.path.join(timestep_dir, "data")):
        raise Exception(f'There is no .fq files in {timestep_dir}')
    if not os.path.exists(path_to_reference_file):
        raise Exception(f'There is no reference genome at {path_to_reference_file}')
    
    CFGS = os.path.join(timestep_dir, "config")
    if not os.path.exists(CFGS):
        os.mkdir(CFGS)

    YAML_ = f"""
    samples: "config/samples.csv"

    reference:
        name: "BA000007_3"
        source: "{path_to_reference_file}"

    reads:
        mark_duplicates: true

    variant_calling:
        expected_coverage: "low"
        tool: "gatk"
        ploidy: 1
        gatk:
            het_prior: 0.005
            concat_batch_size: 5
            concat_max_rounds: 20

    intervals:
        enabled: true
        min_nmer: 500
        num_gvcf_intervals: 2
        db_scatter_factor: 0.15

    callable_sites:
        generate_bed_file: false
        coverage:
            enabled: false
        mappability:
            enabled: true
            kmer: 150
            min_score: 1
            merge_distance: 100

    modules:
        qc:
            enabled: false
        postprocess:
            enabled: false
        trackhub:
            enabled: false
        mk:
            enabled: false
    """
    # Write yaml
    with open(os.path.join(CFGS, "config.yaml"), 'w') as f:
        f.write(YAML_)
    
    DATA = os.path.join(timestep_dir, "data")
    samsheet = make_sample_content(
        "BA000007.3", "fastq", 
        get_all_pair_combinations([f for f in Path(DATA).iterdir() if f.is_dir()])
    )

    with open(os.path.join(CFGS, "samples.csv"), 'w') as f:
        f.write(samsheet)
    

    
def get_all_pair_combinations(paired_fastqs_dir : list) -> list[str]:
    """
    :param:paired_fastqs_dir: a list of all fastq files in the directory
    :rtype:list
    """
    # Get all combinations of 2 files
    result = []
    for fastqs_pair_dir in paired_fastqs_dir:
        fqs = Path(fastqs_pair_dir).glob("*.fq")
        if len(list(fqs)) < 2:
            print(f"Directory {fastqs_pair_dir} does not contain a double-ended read.")
            sys.exit(1)
        
        two_reads = [
            f"{f.resolve().parent.parent.name}/{f.resolve().parent.name}/{f.resolve().name}" 
            for f in Path(fastqs_pair_dir).glob("*.fq")
        ]
        
        string = ";".join(two_reads)
        result.append(string)
    return result

def make_sample_content(sample_id: str, input_type: str, input: list[str]) -> str:
    """
    :param:sample_id: the sample id to write to the sample sheet
    :param:input_type: the type of input (fastq, bam, etc.)
    :param:input: a list of input files for the sample
    :rtype:str
    """
    # Possible headers
    HEADERS = ["sample_id", "input_type", "input"]
    # Create a dataframe
    df = pd.DataFrame(columns=HEADERS)
    # Add every single pair combination to each row
    for i, pair in enumerate(input):
        new_row = pd.DataFrame([[f'{sample_id}.{i}', input_type, pair]], columns=HEADERS)
        df = pd.concat([df, new_row], ignore_index=True)
    # Convert df to csv
    return df.to_csv(index=False)

if __name__ == '__main__':
    generate_time_series_sequences(20, 10)
            