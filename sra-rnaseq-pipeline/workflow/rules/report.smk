rule multiqc_all:
    input:
        expand(f"{TRIMMED_DIR}" + "/fastqc/{{sra_run}}_fastqc.html", sra_run=SRA_RUNS),
        expand(f"{TRIMMED_DIR}" + "/fastqc/{{sra_run}}.trimmed_fastqc.html", sra_run=SRA_RUNS)
    output:
        f"{REPORT_DIR}/multiqc_report.html"
    conda:
        "envs/multiqc.yml"
    shell:
        r"""
        set -euo pipefail
        mkdir -p {REPORT_DIR}
        multiqc {OUTPUT_DIR} --outdir {REPORT_DIR} --filename multiqc_report.html
        """


rule summary_plots:
    input:
        counts=f"{COUNTS_DIR}/expression_matrix.tsv",
        samples="config/samples.csv"
    output:
        library=f"{REPORT_DIR}/plots/library_sizes.png",
        pca=f"{REPORT_DIR}/plots/pca.png"
    params:
        make_pca=config["report"].get("make_pca", True)
    shell:
        r"""
        python scripts/summarize_qc.py \
            --samples {input.samples} \
            --quant {input.counts} \
            --outdir {REPORT_DIR}/plots \
            --make_pca {params.make_pca}
        """
