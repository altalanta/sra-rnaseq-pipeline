rule quantify_expression:
    input:
        fastq=lambda wildcards: f"{TRIMMED_DIR}/{SAMPLE_TO_RUN[wildcards.sample_id]}.trimmed.fastq.gz"
    output:
        quant=f"{QUANT_DIR}" + "/{sample_id}/quant.sf"
    params:
        index=config["genome"]["salmon_index"]
    threads: config["threads"]
    log:
        f"{QUANT_DIR}" + "/{sample_id}/salmon.log"
    conda:
        "envs/salmon.yml"
    shell:
        r"""
        set -euo pipefail
        mkdir -p {QUANT_DIR}/{wildcards.sample_id}
        salmon quant \
            -i {params.index} \
            -l A \
            -r {input.fastq} \
            -p {threads} \
            --gcBias \
            --validateMappings \
            -o {QUANT_DIR}/{wildcards.sample_id} \
            >> {log} 2>&1
        """
