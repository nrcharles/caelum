"""Unit tests."""
import unittest


class BaseEERETest(unittest.TestCase):

    """Annual GHI."""

    def runTest(self):
        """GHI."""
        from caelum import eere
        SCODE = '063800'
        annual_ghi = sum([float(i['GHI (W/m^2)'])
                         for i in eere.EPWdata(SCODE)])
        SCODE = '724666'
        annual_ghi2 = sum([float(i['GHI (W/m^2)'])
                          for i in eere.EPWdata(SCODE)])
        print annual_ghi2
        self.assertAlmostEquals(annual_ghi, 985289)


class eereDesign(unittest.TestCase):

    """Design constrains."""

    def runTest(self):
        """Min/Max temps."""
        from caelum import eere
        SCODE = '063800'
        self.assertAlmostEquals(eere.minimum(SCODE), -10.2)
        self.assertAlmostEquals(eere.twopercent(SCODE), 25.4)
        SCODE = '724666'
        self.assertAlmostEquals(eere.minimum(SCODE), -22.9)
        self.assertAlmostEquals(eere.twopercent(SCODE), 30.2)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BaseEERETest)
    unittest.TextTestRunner(verbosity=2).run(suite)
