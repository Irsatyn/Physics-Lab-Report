import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'physics-lab-report' / 'scripts'))
from plot_xy import calculate


class PlotTests(unittest.TestCase):
    def test_fit_is_stable_under_large_x_translation(self):
        result = calculate([1e9, 1e9+1, 1e9+2, 1e9+3], [1, 3, 5, 7], fit=True)
        self.assertAlmostEqual(result['slope'], 2)
        self.assertAlmostEqual(result['intercept'], 1-2e9)
        self.assertAlmostEqual(result['r_squared'], 1)
        self.assertAlmostEqual(result['residual_std'], 0)

    def test_fit_matches_known_physics_example(self):
        result = calculate([1, 2, 3, 4], [3, 5, 7, 9], fit=True)
        self.assertAlmostEqual(result['slope'], 2)
        self.assertAlmostEqual(result['intercept'], 1)
        self.assertAlmostEqual(result['r_squared'], 1)

    def test_invalid_measurements_are_not_silently_dropped(self):
        for x, y in [([1, 2], [2, float('nan')]), ([1, 2], [1]), ([1], [2])]:
            with self.assertRaises(ValueError):
                calculate(x, y)
        with self.assertRaises(ValueError):
            calculate([1, 1, 1], [2, 3, 4], fit=True)
        self.assertFalse(calculate([1, 2], [3, 5])['fit'])


if __name__ == '__main__':
    unittest.main()
