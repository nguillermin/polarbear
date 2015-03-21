import unittest
import automator

class TestSequenceFunctions(unittest.TestCase):
    
    def test_split_voltages(self):
        """Makes sure the split_voltages functions return properly
            split voltages"""
        positive = range(10) 
        self.assertEqual(([],positive),automator.split_voltages(positive))
        negative = range(-10,0)
        self.assertEqual((negative,[]),automator.split_voltages(negative))
        straddle = range(-10,10)
        self.assertEqual(([-10,-9,-8,-7,-6,-5,-4,-3,-2,-1],[0,1,2,3,4,5,6,7,8,9]),automator.split_voltages(straddle))
        
    def test_save_multiple(self):
        """Ensures multiple data sets are written in columnar csv format"""
        dataset_1 = {k: [200, 1e-5] for k in range(-4,4)}
        dataset_2 = {k: [20, 1.5e-5] for k in range(-3,5)}
        dataset_3 = {k: [2000, 2e-5] for k in range(-4,5)}
        

if __name__=='__main__':
    unittest.main()

