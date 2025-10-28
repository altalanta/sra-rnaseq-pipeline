rule merge_counts:
    input:
        expand(f"{QUANT_DIR}" + "/{sample_id}/quant.sf", sample_id=SAMPLE_IDS)
    output:
        f"{COUNTS_DIR}/expression_matrix.tsv"
    shell:
        r"""
        python scripts/make_counts_matrix.py \
            --quant_dir {QUANT_DIR} \
            --out {output}
        """
