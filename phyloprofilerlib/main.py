import argparse
import subprocess
import os
import sys

def check_file_exists_or_die(file_name):
    if not os.path.isfile(file_name):
        print "ERROR: file " + file_name + " does not exist: check the file name and path."
        sys.exit(1)

def run_command(command, error_message):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print error_message

def get_args(argv):
    parser = argparse.ArgumentParser(description="Runs Metaphlan2.")
    parser.add_argument("--forward-reads", required=True,
                        type=argparse.FileType("r"),
                        help="R1.fastq")
    parser.add_argument("--reverse-reads", required=True,
                        type=argparse.FileType("r"),
                        help="R2.fastq")
    parser.add_argument("--output-file", required=True,
                        type=argparse.FileType("w"),
                        help="output file")
    args = parser.parse_args(argv)
    check_file_exists_or_die(args.forward-reads.name)
    check_file_exists_or_die(args.reverse-reads.name)
    args.forward-reads.close()
    args.reverse-reads.close()
    args.output-file.close()
    return(args)

def run_metaphlan(R1, R2, output):
    command = ("python /home/ashwini/ash/other_softwares/metaphlan2/metaphlan2.py " + R1 + "," + R2 +
               " --mpa_pkl " + "/home/ashwini/ash/other_softwares/metaphlan2/db_v20/mpa_v20_m200.pkl" +
               " --bowtie2db /home/ashwini/ash/other_softwares/metaphlan2/db_v20/mpa_v20_m200" +
               " --bowtie2out " + output + ".bowtie2.bz2" +
               " --nproc 5" +
               " --input_type fastq > " + output)
    run_command(command, "Cannot run MetaPhlAn2. Check input files")

def main(argv=None):
    args = get_args(argv)
    run_metaphlan(args.forward-reads.name, args.reverse-reads.name, args.output-file.name)

if __name__=="__main__":
    main()
