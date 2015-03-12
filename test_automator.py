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

if __name__=='__main__':
    unittest.main()

