import argparse
import distutils.spawn
import subprocess
import os
import sys
import json

from phyloprofilerlib.version import __version__


def get_config(user_config_file):
    config = {
        "metaphlan_fp": "metaphlan2.py",
        "mpa_pkl": "mpa_v20_m200.pkl",
        "bowtie2db": "mpa_v20_m200",
        "bowtie2_fp": "bowtie2",
        "temp_dir": ""
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

    if user_config_file is None:
        default_user_config_fp = os.path.expanduser("~/.phylogenetic_profiler.json")
        if os.path.exists(default_user_config_fp):
            user_config_file = open(default_user_config_fp)

    if user_config_file is not None:
        user_config = json.load(user_config_file)
        config.update(user_config)

    return config


class Metaphlan(object):
    def __init__(self, config):
        self.config = config

    def make_command(self, R1, R2, out_dir):
        return [
            "python", self.config["metaphlan_fp"],
            "%s,%s" %(R1, R2),
            "--mpa_pkl", self.config["mpa_pkl"],
            "--bowtie2db", self.config["bowtie2db"],
            "--bowtie2_exe", self.config["bowtie2_fp"],
            "--bowtie2out", self.make_db_out_fp(R1, out_dir),
            "--input_type", "fastq" ,
            "--tmp_dir", self.config["temp_dir"] ]
    
    def make_db_out_fp(self, R1, out_dir):
        return os.path.join(out_dir, "%s.bowtie2" % os.path.splitext(os.path.basename(R1))[0])
    
    def make_output_handle(self, R1, out_dir):
        return open(os.path.join(out_dir, "%s.txt" % os.path.splitext(os.path.basename(R1))[0]), 'w')

    def run(self, R1, R2, out_dir):
        command = self.make_command(R1, R2, out_dir)
        output = subprocess.check_output(command)
        revised_output = self.revise_output(output)
        #revised_output = output
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

    config = get_config(args.config_file)

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


