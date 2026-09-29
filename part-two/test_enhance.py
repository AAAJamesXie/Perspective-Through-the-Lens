"""Behavior tests for the three optional restoration methods; no mocks."""
import unittest
import numpy as np
import enhance


class EnhancementTests(unittest.TestCase):
    def test_detects_variable_black_white_and_colored_borders(self):
        content = np.random.default_rng(3).uniform(.25, .75, (80, 100, 3)).astype('float32')
        for color in ([0, 0, 0], [1, 1, 1], [.8, .1, .4]):
            for top, bottom, left, right in [(4, 7, 5, 9), (8, 3, 11, 2)]:
                with self.subTest(color=color, margins=(top, bottom, left, right)):
                    a = np.empty((80+top+bottom, 100+left+right, 3), np.float32)
                    a[:] = color
                    a[top:top+80, left:left+100] = content
                    cropped, info = enhance.auto_crop(a)
                    self.assertEqual(info['box_xyxy'], [left, top, left+100, top+80])
                    np.testing.assert_array_equal(cropped, content)

    def test_unbordered_texture_and_constant_image_are_preserved(self):
        for a in (np.random.default_rng(8).uniform(.2, .8, (80, 100, 3)),
                  np.full((60, 80, 3), .4)):
            result, _ = enhance.auto_crop(a)
            np.testing.assert_allclose(result, a)

    def test_contrast_uses_shared_endpoints(self):
        a = np.linspace(.2, .8, 300).reshape(10, 10, 3).astype('float32')
        result, _ = enhance.auto_contrast(a, percentiles=(0, 100))
        np.testing.assert_allclose(result, (a-.2)/.6, atol=2e-7)
        self.assertAlmostEqual(float(result.min()), 0)
        self.assertAlmostEqual(float(result.max()), 1)

    def test_gray_world_removes_known_cast_without_mutating_input(self):
        gray = np.linspace(.1, .5, 100).reshape(10, 10, 1)
        a = (gray * [1.4, 1, .7]).astype('float32')
        original = a.copy()
        result, info = enhance.white_balance(a)
        np.testing.assert_allclose(result[..., 0], result[..., 1], atol=1e-7)
        np.testing.assert_allclose(result[..., 1], result[..., 2], atol=1e-7)
        self.assertEqual(len(info['gains_rgb']), 3)
        np.testing.assert_array_equal(a, original)

    def test_constant_and_zero_channel_outputs_are_finite(self):
        for a in (np.zeros((12, 16, 3)), np.full((12, 16, 3), .4),
                  np.tile([0, .3, .6], (12, 16, 1))):
            for fn in (enhance.auto_contrast, enhance.white_balance):
                result, _ = fn(a)
                self.assertTrue(np.isfinite(result).all())
                self.assertGreaterEqual(result.min(), 0)
                self.assertLessEqual(result.max(), 1)
            result, _ = enhance.auto_contrast(a)
            if np.ptp(a) == 0:
                np.testing.assert_allclose(result, a)

    def test_invalid_images_are_rejected(self):
        for a in (np.zeros((2, 3)), np.zeros((0, 4, 3)),
                  np.full((2, 3, 3), np.nan), np.full((2, 3, 3), 1.2)):
            for fn in (enhance.auto_crop, enhance.auto_contrast, enhance.white_balance):
                with self.assertRaises(ValueError):
                    fn(a)


if __name__ == '__main__':
    unittest.main()
