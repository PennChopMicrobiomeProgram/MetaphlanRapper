import argparse
import distutils.spawn
import subprocess
import os
import sys
import json

from phyloprofilerlib.version import __version__


def make_default_config():
    config = {
        "metaphlan_fp": "metaphlan2.py",
        "mpa_pkl": "mpa_v20_m200.pkl",
        "bowtie2db": "mpa_v20_m200",
        "bowtie2_fp": "bowtie2",
    }
    metaphlan_fp = distutils.spawn.find_executable("metaphlan2.py")
    if metaphlan_fp is not None:
        # If the metaphlan2.py script is found in our path, we look
        # for metaphlan2 data in the directory containing the
        # script.  Otherwise, we assume the metaphlan2 script and
        # data are in the current directory.
        metaphlan_dir = os.path.dirname(metaphlan_fp)
        config.update({
            "metaphlan_fp": metaphlan_fp,
            "mpa_pkl": os.path.join(metaphlan_dir, "db_v20", "mpa_v20_m200.pkl"),
            "bowtie2db": os.path.join(metaphlan_dir, "db_v20", "mpa_v20_m200"),
        })
    bowtie2_fp = distutils.spawn.find_executable("bowtie2")
    if bowtie2_fp is not None:
        config.update({"bowtie2_fp": bowtie2_fp})
    return config


class Metaphlan(object):
    def __init__(self, config):
        self.config = config

    def make_command(self, R1, R2):
        return [
            "python", self.config["metaphlan_fp"],
            "%s,%s" %(R1, R2),
            "--mpa_pkl", self.config["mpa_pkl"],
            "--bowtie2db", self.config["bowtie2db"],
            "--bowtie2_exe", self.config["bowtie2_fp"],
            "--no_map",
            "--input_type", "fastq"]
    
    def make_output_handle(self, R1, out_dir):
        return open(os.path.join(out_dir, "%s.txt" % os.path.splitext(os.path.basename(R1))[0]), 'w')

    def run(self, R1, R2, out_dir):
        command = self.make_command(R1, R2)
        output = subprocess.check_output(command)
        revised_output = self.revise_output(output)
        with self.make_output_handle(R1, out_dir) as f:
            f.write(revised_output)

    @staticmethod
    def revise_output(output):
        output_lines = output.splitlines(True)
        if len(output_lines) < 2:
            raise ValueError("Output has fewer than 2 lines.")
        elif len(output_lines) == 2:
            return output
        else:
            header = output_lines.pop(0)
            revised_output_lines = [header]
            for line in output_lines:
                if ("s__" in line) and not ("t__" in line):
                    revised_output_lines.append(line)
            return "".join(revised_output_lines)


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

    config = make_default_config()
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


