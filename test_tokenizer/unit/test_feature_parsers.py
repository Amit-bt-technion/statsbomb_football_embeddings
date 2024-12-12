import unittest
from parameterized import parameterized
from tokenizer.feature_parsers import (
    CategoricalFeatureParser,
    RangeFeatureParser,
    PassRecipientFeatureParser,
    FreezeFrameFeaturesParser
)


class TestTokenizer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @parameterized.expand([
        ([0, 1], [0.5, 1]),
        ([12, 58], [0.5, 1]),
        ([809, 58], [1, 0.5]),
        ([41, 1, 2, 100], [0.75, 0.25, 0.5, 1]),
    ])
    def test_categorical_feature_parser(self, categories, expected):
        parser = CategoricalFeatureParser("test parser", categories)
        for i, elem in enumerate(categories):
            self.assertEquals(parser.get_normalized(elem), expected[i])

    def test_range_feature_parser(self):
        pass

    def test_pass_recipient_feature_parser(self):
        pass

    def test_freeze_frame_features_parser(self):
        pass
