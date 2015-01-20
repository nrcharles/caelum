import unittest
class BaseEERETest(unittest.TestCase):
    def runTest(self):
        from caelum import eree
        SCODE = '063800'
        annual_ghi = sum([float(i['GHI (W/m^2)']) for i in eree.EPWdata(SCODE)])
        SCODE = '724666'
        annual_ghi2 = sum([float(i['GHI (W/m^2)']) for i in eree.EPWdata(SCODE)])
        print annual_ghi2
        self.assertAlmostEquals(annual_ghi, 985289)

class EREEDesign(unittest.TestCase):
    def runTest(self):
        from caelum import eree
        SCODE = '063800'
        self.assertAlmostEquals(eree.minimum(SCODE),-10.2)
        self.assertAlmostEquals(eree.twopercent(SCODE),25.4)
        SCODE = '724666'
        self.assertAlmostEquals(eree.minimum(SCODE),-22.9)
        self.assertAlmostEquals(eree.twopercent(SCODE),30.2)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BaseEERETest)
    unittest.TextTestRunner(verbosity=2).run(suite)
