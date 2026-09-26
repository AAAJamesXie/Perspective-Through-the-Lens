"""Real synthetic-image unit tests; no mocks or external data."""
import unittest
import numpy as np

from colorize import split_plate, search_shift, pyramid_align, compose, normalize


class ColorizeTests(unittest.TestCase):
    def test_split_bgr_and_trailing_rows(self):
        plate = np.vstack([np.full((12, 15), v, np.uint8) for v in (10, 20, 30)])
        plate = np.vstack([plate, np.full((2, 15), 255, np.uint8)])
        b, g, r = split_plate(plate)
        self.assertEqual(b.shape, (12, 15))
        self.assertAlmostEqual(float(b[0, 0]), 10/255)
        self.assertAlmostEqual(float(g[0, 0]), 20/255)
        self.assertAlmostEqual(float(r[0, 0]), 30/255)

    def test_uint16_normalization_preserves_range(self):
        a = normalize(np.array([[0, 32768, 65535]], np.uint16))
        np.testing.assert_allclose(a, [[0, 32768/65535, 1]], atol=1e-7)

    def test_search_recovers_applied_shift_for_both_metrics(self):
        b = np.random.default_rng(7).random((95, 111), dtype=np.float32)
        g = np.roll(b, (4, -7), (0, 1))
        for metric in ('ncc', 'l2'):
            with self.subTest(metric=metric):
                shift, score = search_shift(b, g, radius=9, metric=metric)
                self.assertEqual(shift, (7, -4))
                self.assertTrue(np.isfinite(score))

    def test_pyramid_recovers_large_shift_on_odd_dimensions(self):
        # Random low-frequency structure survives antialiased downsampling.
        from PIL import Image
        coarse = np.random.default_rng(12).random((60, 65), dtype=np.float32)
        b = np.asarray(Image.fromarray(coarse).resize((517, 481), Image.Resampling.BICUBIC))
        g = np.roll(b, (-26, 39), (0, 1))
        shift, trace = pyramid_align(b, g, min_size=96)
        self.assertEqual(shift, (-39, 26))
        self.assertGreater(len(trace), 1)
        self.assertEqual(trace[-1]['shift_xy'], [-39, 26])

    def test_composition_uses_rgb_and_removes_wrapped_pixels(self):
        b = np.arange(120, dtype=np.float32).reshape(10, 12)/200
        g = np.roll(b + .1, (2, -3), (0, 1))
        r = np.roll(b + .2, (-1, 2), (0, 1))
        rgb = compose(b, g, r, (3, -2), (-2, 1), crop=True)
        self.assertEqual(rgb.shape, (7, 7, 3))
        np.testing.assert_allclose(rgb[:, :, 0], b[1:8, 3:10]+.2)
        np.testing.assert_allclose(rgb[:, :, 1], b[1:8, 3:10]+.1)
        np.testing.assert_allclose(rgb[:, :, 2], b[1:8, 3:10])

    def test_constant_images_prefer_zero_when_tied(self):
        b = np.ones((50, 60), np.float32)
        self.assertEqual(search_shift(b, b, radius=5)[0], (0, 0))
        self.assertEqual(search_shift(b*0, b*0, radius=5)[0], (0, 0))

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            split_plate(np.zeros((2, 10), np.uint8))
        with self.assertRaises(ValueError):
            search_shift(np.zeros((20, 20)), np.zeros((21, 20)))
        with self.assertRaises(ValueError):
            search_shift(np.zeros((20, 20)), np.zeros((20, 20)), radius=-1)
        with self.assertRaises(ValueError):
            normalize(np.array([[float('nan')]]))


if __name__ == '__main__':
    unittest.main()
