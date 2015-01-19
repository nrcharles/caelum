import unittest
class BaseEERETest(unittest.TestCase):
    def runTest(self):
        from caelum import eree
        SCODE = '063800'
        annual_ghi = sum([float(i['GHI (W/m^2)']) for i in eree.EPWdata(SCODE)])
        self.assertAlmostEquals(annual_ghi, 985289)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BaseEERETest)
    unittest.TextTestRunner(verbosity=2).run(suite)
