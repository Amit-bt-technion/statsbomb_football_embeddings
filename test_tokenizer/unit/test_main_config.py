import unittest
from tokenizer import event_types_mapping,  vector_size, event_ids
# important - test no intersecting intervals between index ranges


class TestMainConfig(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_event_ids_exist(self):
        for event_id in event_ids.values():
            self.assertIsNotNone(event_types_mapping[event_id])
        for event_id in event_types_mapping.keys():
            if type(event_id) == int:
                self.assertIn(event_id, event_ids.values())

    def test_index_ranges(self):
        """
        tests that the indexes of the target features in the vector do not intersect and sum up to vector length and
        that all indexes belong to a range
        """
        intervals = []
        for config in event_types_mapping.values():
            num_of_features = len(config["feature_parsers"])
            num_of_special_features = config.get("num_of_special_features", 0)
            if num_of_features == 0:
                continue
            start = config["starting_index"]
            # subtracting 1 for interval to be inclusive on both ends
            end = start + num_of_features - 1
            intervals.append((start, end, ))
            if num_of_special_features > 0:
                # not adding 1 to the end interval for it to be inclusive on both ends
                intervals.append((end + 1, end + num_of_special_features, ))

        # O(N^2) basic intersection validation - N = O(1)
        num_of_intervals = len(intervals)
        for i in range(num_of_intervals):
            current_start, current_end = intervals[i][0], intervals[i][1]
            j = i + 1
            while j < num_of_intervals:
                other_interval_start, other_interval_end = intervals[j][0], intervals[j][1]
                # if current interval starts before the other, assert that it also ends before the other starts
                if current_start <= other_interval_start:
                    self.assertLess(current_end, other_interval_start)
                # otherwise, current starts after the other, assert that it also starts after the other ends
                else:
                    self.assertGreater(current_start, other_interval_end)
                j = j + 1

        # create a boolean mapping for indexes mapped by an interval
        used_indexes = [False for _ in range(vector_size)]
        for (interval_start, interval_end) in intervals:
            # adding 1 as the interval is inclusive
            for i in range(interval_start, interval_end + 1):
                used_indexes[i] = True

        # make sure all values are true
        self.assertTrue(all(used_indexes))

