import json
import os
import shutil
import tempfile
import unittest

from phyloprofilerlib.main import Metaphlan, main


class MetaphlanWrapperTest(unittest.TestCase):
    def setUp(self):
        self.config = {
            "metaphlan_fp": "metaphlan2.py",
            "mpa_pkl": "mpa_v20_m200.pkl",
            "bowtie2db": "mpa_v20_m200",
        }
        self.r1 = "fake_genome1-R1.fastq"
        self.r2 = "fake_genome1-R2.fastq"
        self.out = "out"

    def test_main(self):
        app = Metaphlan(self.config)
        observed = app.make_command(self.r1, self.r2)
        expected = [
            'python', 'metaphlan2.py',
            'fake_genome1-R1.fastq,fake_genome1-R2.fastq',
            '--mpa_pkl', 'mpa_v20_m200.pkl',
            '--bowtie2db', 'mpa_v20_m200',
            '--nproc', '5',
            '--bowtie2out', 'out.bowtie2.bz2',
            '--input_type', 'fastq',
        ]
        self.assertEqual(observed, expected)


class MainTests(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.output_dir)

    def test_main_function(self):
        r1 = tempfile.NamedTemporaryFile(suffix=".fastq")
        r2 = tempfile.NamedTemporaryFile(suffix=".fastq")

        metaphlan_dir = \
            "/Users/bittingerk/Software/biobakery-metaphlan2-901cc5778eed"
        config = {
            "metaphlan_fp": os.path.join(metaphlan_dir, "metaphlan2.py"),
            "mpa_pkl": os.path.join(metaphlan_dir, "db_v20", "mpa_v20_m200.pkl"),
            "bowtie2db": os.path.join(metaphlan_dir, "db_v20", "mpa_v20_m200"),
        }
        
        config_file = tempfile.NamedTemporaryFile(suffix=".json")
        json.dump(config, config_file)
        config_file.seek(0)

        summary_fp = os.path.join(self.output_dir, "summary.txt")
        output_fp = os.path.join(self.output_dir, "output.txt")
        args = [
            "--forward-reads", r1.name,
            "--reverse-reads", r2.name,
            "--summary-file", summary_fp,
            "--output-file", output_fp,
            "--config-file", config_file.name,
        ]
        main(args)

        # Then test the output
        
if __name__=="__main__":
    unittest.main()
