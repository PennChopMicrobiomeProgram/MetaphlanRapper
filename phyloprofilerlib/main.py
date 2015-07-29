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
            "--tax_lev", "s",
            "--mpa_pkl", self.config["mpa_pkl"],
            "--bowtie2db", self.config["bowtie2db"],
            "--no_map",
            "--nproc", "5",
            "--input_type", "fastq"]
    
    def make_output_handle(self, R1, out_dir):
        return open(os.path.join(out_dir, "%s.txt" % os.path.splitext(os.path.basename(R1))[0]), 'w')

    def run(self, R1, R2, out_dir):
        command = self.make_command(R1, R2)
        subprocess.check_call(command, stdout=self.make_output_handle(R1, out_dir), stderr=subprocess.STDOUT)


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
        "--output-dir", required=True,
        help="output directory")
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

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    app = Metaphlan(config)
    app.run(fwd_fp, rev_fp, args.output_dir)
    save_summary(args.summary_file, config)

def save_summary(f, config):
    result = {
        "program": "PhyloProfiler",
        "version": __version__,
        "config": config
        }
    json.dump(result, f)


