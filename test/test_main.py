import unittest
import os

from phyloprofilerlib.main import Metaphlan


class MetaphlanWrapperTest(unittest.TestCase):
    def setUp(self):
        self.config = {
            "metaphlan_fp": "metaphlan2.py",
            "mpa_pkl": "pa_v20_m200.pkl",
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
            '--mpa_pkl', 'pa_v20_m200.pkl',
            '--bowtie2db', 'mpa_v20_m200',
            '--nproc', '5',
            '--bowtie2out', 'out.bowtie2.bz2',
            '--input_type', 'fastq',
        ]
        self.assertEqual(observed, expected)

if __name__=="__main__":
    unittest.main()
