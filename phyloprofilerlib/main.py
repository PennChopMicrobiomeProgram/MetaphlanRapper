import argparse
import subprocess
import os
import sys
import json

from phyloprofilerlib.version import __version__

default_config ={
    "metaphlan_fp": "/home/ashwini/ash/other_softwares/metaphlan2/metaphlan2.py",
    "mpa_pkl": "/home/ashwini/ash/other_softwares/metaphlan2/db_v20/mpa_v20_m200.pkl",
    "bowtie2db": "/home/ashwini/ash/other_softwares/metaphlan2/db_v20/mpa_v20_m200"
    }

class Metaphlan(object):
    def __init__(self, config):
        self.config = config

    def make_command(self, R1, R2):
        return [
            "python", self.config["metaphlan_fp"],
            "%s,%s" %(R1, R2),
            "--mpa_pkl", self.config["mpa_pkl"],
            "--bowtie2db", self.config["bowtie2db"],
            "--nproc", "5",
            "--bowtie2out", "out.bowtie2.bz2",
            "--input_type", "fastq"]

    def run(self, R1, R2, output):
        command = self.make_command(R1, R2)
        subprocess.check_call(command, stdout=output, stderr=subprocess.STDOUT)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Runs Metaphlan2.")
    parser.add_argument(
        "--forward-reads", required=True,
        type=argparse.FileType("r"),
        help="R1.fastq")
    parser.add_argument(
        "--reverse-reads", required=True,
        type=argparse.FileType("r"),
        help="R2.fastq")
    parser.add_argument(
        "--summary-file", required=True,
        type=argparse.FileType("w"),
        help="Summary file")
    parser.add_argument(
        "--output-file", required=True,
        help="output file")
    parser.add_argument(
        "--config-file",
        type=argparse.FileType("r"),
        help="JSON configuration file")
    args = parser.parse_args(argv)

    config = default_config.copy()
    if args.config_file:
        user_config = json.load(args.config_file)
        config.update(user_config)

    fwd_fp = args.forward_reads.name
    rev_fp = args.reverse_reads.name
    args.forward_reads.close()
    args.reverse_reads.close()

    app = Metaphlan(config)
    app.run(fwd_fp, rev_fp, open(args.output_file, "w"))
    save_summary(args.summary_file, config)

def save_summary(f, config):
    result = {
        "program": "PhyloProfiler",
        "version": __version__,
        "config": config
        }
    json.dump(result, f)


