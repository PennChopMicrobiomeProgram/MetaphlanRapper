import unittest
import metaphlan_wrapper
import os

class MetaphlanWrapperTest(unittest.TestCase):
    def setUp(self):
        self.r1 = "fake_genome1-R1.fastq"
        self.r2 = "fake_genome1-R2.fastq"
        self.out = "out"
       
  
    def test_main(self):
        metaphlan_wrapper.run_metaphlan(self.r1, self.r2, self.out)
        self.assertTrue(os.path.isfile(self.out + ".txt"))

if __name__=="__main__":
    unittest,main()
