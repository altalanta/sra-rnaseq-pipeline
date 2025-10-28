rule download_fastq:
    input:
        sra_run=lambda wildcards: wildcards.sra_run
    output:
        fastq=f"{RAW_FASTQ_DIR}" + "/{sra_run}.fastq.gz"
    log:
        f"{RAW_FASTQ_DIR}" + "/{sra_run}.log.txt"
    threads: config["threads"]
    shell:
        r"""
        set -euo pipefail
        tmpdir=$(mktemp -d)
        trap 'rm -rf "$tmpdir"' EXIT
        fasterq-dump --threads {threads} --outdir "$tmpdir" {wildcards.sra_run} >> {log} 2>&1
        gzip -c "$tmpdir"/{wildcards.sra_run}.fastq > {output.fastq}
        echo "Compressed FASTQ written to {output.fastq}" >> {log}
        """
