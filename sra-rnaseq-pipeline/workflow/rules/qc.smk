rule trim_qc:
    input:
        raw=f"{RAW_FASTQ_DIR}" + "/{sra_run}.fastq.gz"
    output:
        trimmed=f"{TRIMMED_DIR}" + "/{sra_run}.trimmed.fastq.gz"
    log:
        f"{TRIMMED_DIR}" + "/{sra_run}.fastp.log"
    threads: config["threads"]
    params:
        min_length=config["qc"]["min_read_length"],
        adapter_flag="" if config["adapter_trimming"] else "--disable_adapter_trimming"
    shell:
        r"""
        set -euo pipefail
        mkdir -p {TRIMMED_DIR}/fastp
        fastp \
            --in1 {input.raw} \
            --out1 {output.trimmed} \
            --length_required {params.min_length} \
            --thread {threads} \
            --html {TRIMMED_DIR}/fastp/{wildcards.sra_run}.fastp.html \
            --json {TRIMMED_DIR}/fastp/{wildcards.sra_run}.fastp.json \
            {params.adapter_flag} \
            >> {log} 2>&1
        """


rule fastqc_report:
    input:
        raw=f"{RAW_FASTQ_DIR}" + "/{sra_run}.fastq.gz",
        trimmed=f"{TRIMMED_DIR}" + "/{sra_run}.trimmed.fastq.gz"
    output:
        raw_html=f"{TRIMMED_DIR}" + "/fastqc/{{sra_run}}_fastqc.html",
        raw_zip=f"{TRIMMED_DIR}" + "/fastqc/{{sra_run}}_fastqc.zip",
        trimmed_html=f"{TRIMMED_DIR}" + "/fastqc/{{sra_run}}.trimmed_fastqc.html",
        trimmed_zip=f"{TRIMMED_DIR}" + "/fastqc/{{sra_run}}.trimmed_fastqc.zip"
    threads: 2
    conda:
        "envs/fastqc.yml"
    shell:
        r"""
        set -euo pipefail
        mkdir -p {TRIMMED_DIR}/fastqc
        fastqc --threads {threads} --outdir {TRIMMED_DIR}/fastqc {input.raw} {input.trimmed}
        """
