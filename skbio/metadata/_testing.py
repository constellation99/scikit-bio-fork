# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import copy

import pandas as pd
import numpy as np
import numpy.testing as npt

from skbio.util._testing import assert_data_frame_almost_equal


class MetadataMixinTests:
    def test_constructor_invalid_type(self):
        for md in (0, 'a', ('f', 'o', 'o'), np.array([]), pd.DataFrame()):
            with self.assertRaisesRegex(TypeError, 'metadata must be a dict'):
                self._metadata_constructor_(metadata=md)

    def test_constructor_no_metadata(self):
        for md in None, {}:
            obj = self._metadata_constructor_(metadata=md)

            self.assertFalse(obj.has_metadata())
            self.assertEqual(obj.metadata, {})

    def test_constructor_with_metadata(self):
        obj = self._metadata_constructor_(metadata={'foo': 'bar'})
        self.assertEqual(obj.metadata, {'foo': 'bar'})

        obj = self._metadata_constructor_(
                metadata={'': '', 123: {'a': 'b', 'c': 'd'}})
        self.assertEqual(obj.metadata, {'': '', 123: {'a': 'b', 'c': 'd'}})

    def test_constructor_handles_missing_metadata_efficiently(self):
        self.assertIsNone(self._metadata_constructor_()._metadata)
        self.assertIsNone(self._metadata_constructor_(metadata=None)._metadata)

    def test_constructor_makes_shallow_copy_of_metadata(self):
        md = {'foo': 'bar', 42: []}
        obj = self._metadata_constructor_(metadata=md)

        self.assertEqual(obj.metadata, md)
        self.assertIsNot(obj.metadata, md)

        md['foo'] = 'baz'
        self.assertEqual(obj.metadata, {'foo': 'bar', 42: []})

        md[42].append(True)
        self.assertEqual(obj.metadata, {'foo': 'bar', 42: [True]})

    def test_eq(self):
        self.assertReallyEqual(
                self._metadata_constructor_(metadata={'foo': 42}),
                self._metadata_constructor_(metadata={'foo': 42}))

        self.assertReallyEqual(
                self._metadata_constructor_(metadata={'foo': 42, 123: {}}),
                self._metadata_constructor_(metadata={'foo': 42, 123: {}}))

    def test_eq_missing_metadata(self):
        self.assertReallyEqual(self._metadata_constructor_(),
                               self._metadata_constructor_())
        self.assertReallyEqual(self._metadata_constructor_(),
                               self._metadata_constructor_(metadata={}))
        self.assertReallyEqual(self._metadata_constructor_(metadata={}),
                               self._metadata_constructor_(metadata={}))

    def test_eq_handles_missing_metadata_efficiently(self):
        obj1 = self._metadata_constructor_()
        obj2 = self._metadata_constructor_()
        self.assertReallyEqual(obj1, obj2)

        self.assertIsNone(obj1._metadata)
        self.assertIsNone(obj2._metadata)

    def test_ne(self):
        # Both have metadata.
        obj1 = self._metadata_constructor_(metadata={'id': 'foo'})
        obj2 = self._metadata_constructor_(metadata={'id': 'bar'})
        self.assertReallyNotEqual(obj1, obj2)

        # One has metadata.
        obj1 = self._metadata_constructor_(metadata={'id': 'foo'})
        obj2 = self._metadata_constructor_()
        self.assertReallyNotEqual(obj1, obj2)

    def test_copy_metadata_none(self):
        obj = self._metadata_constructor_()
        obj_copy = copy.copy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNone(obj._metadata)
        self.assertIsNone(obj_copy._metadata)

    def test_copy_metadata_empty(self):
        obj = self._metadata_constructor_(metadata={})
        obj_copy = copy.copy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertEqual(obj._metadata, {})
        self.assertIsNone(obj_copy._metadata)

    def test_copy_with_metadata(self):
        obj = self._metadata_constructor_(metadata={'foo': [1]})
        obj_copy = copy.copy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNot(obj._metadata, obj_copy._metadata)
        self.assertIs(obj._metadata['foo'], obj_copy._metadata['foo'])

        obj_copy.metadata['foo'].append(2)
        obj_copy.metadata['foo2'] = 42

        self.assertEqual(obj_copy.metadata, {'foo': [1, 2], 'foo2': 42})
        self.assertEqual(obj.metadata, {'foo': [1, 2]})

    def test_deepcopy_metadata_none(self):
        obj = self._metadata_constructor_()
        obj_copy = copy.deepcopy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNone(obj._metadata)
        self.assertIsNone(obj_copy._metadata)

    def test_deepcopy_metadata_empty(self):
        obj = self._metadata_constructor_(metadata={})
        obj_copy = copy.deepcopy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertEqual(obj._metadata, {})
        self.assertIsNone(obj_copy._metadata)

    def test_deepcopy_with_metadata(self):
        obj = self._metadata_constructor_(metadata={'foo': [1]})
        obj_copy = copy.deepcopy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNot(obj._metadata, obj_copy._metadata)
        self.assertIsNot(obj._metadata['foo'], obj_copy._metadata['foo'])

        obj_copy.metadata['foo'].append(2)
        obj_copy.metadata['foo2'] = 42

        self.assertEqual(obj_copy.metadata, {'foo': [1, 2], 'foo2': 42})
        self.assertEqual(obj.metadata, {'foo': [1]})

    def test_deepcopy_memo_is_respected(self):
        # Basic test to ensure deepcopy's memo is passed through to recursive
        # deepcopy calls.
        obj = self._metadata_constructor_(metadata={'foo': 'bar'})
        memo = {}
        copy.deepcopy(obj, memo)
        self.assertGreater(len(memo), 2)

    def test_metadata_getter(self):
        obj = self._metadata_constructor_(
                metadata={42: 'foo', ('hello', 'world'): 43})

        self.assertIsInstance(obj.metadata, dict)
        self.assertEqual(obj.metadata, {42: 'foo', ('hello', 'world'): 43})

        obj.metadata[42] = 'bar'
        self.assertEqual(obj.metadata, {42: 'bar', ('hello', 'world'): 43})

    def test_metadata_getter_no_metadata(self):
        obj = self._metadata_constructor_()

        self.assertIsNone(obj._metadata)
        self.assertIsInstance(obj.metadata, dict)
        self.assertEqual(obj.metadata, {})
        self.assertIsNotNone(obj._metadata)

    def test_metadata_setter(self):
        obj = self._metadata_constructor_()

        self.assertFalse(obj.has_metadata())

        obj.metadata = {'hello': 'world'}
        self.assertTrue(obj.has_metadata())
        self.assertEqual(obj.metadata, {'hello': 'world'})

        obj.metadata = {}
        self.assertFalse(obj.has_metadata())
        self.assertEqual(obj.metadata, {})

    def test_metadata_setter_makes_shallow_copy(self):
        obj = self._metadata_constructor_()

        md = {'foo': 'bar', 42: []}
        obj.metadata = md

        self.assertEqual(obj.metadata, md)
        self.assertIsNot(obj.metadata, md)

        md['foo'] = 'baz'
        self.assertEqual(obj.metadata, {'foo': 'bar', 42: []})

        md[42].append(True)
        self.assertEqual(obj.metadata, {'foo': 'bar', 42: [True]})

    def test_metadata_setter_invalid_type(self):
        obj = self._metadata_constructor_(metadata={123: 456})

        for md in (None, 0, 'a', ('f', 'o', 'o'), np.array([]),
                   pd.DataFrame()):
            with self.assertRaisesRegex(TypeError, 'metadata must be a dict'):
                obj.metadata = md
            self.assertEqual(obj.metadata, {123: 456})

    def test_metadata_deleter(self):
        obj = self._metadata_constructor_(metadata={'foo': 'bar'})

        self.assertEqual(obj.metadata, {'foo': 'bar'})

        del obj.metadata
        self.assertIsNone(obj._metadata)
        self.assertFalse(obj.has_metadata())

        # Delete again.
        del obj.metadata
        self.assertIsNone(obj._metadata)
        self.assertFalse(obj.has_metadata())

        obj = self._metadata_constructor_()

        self.assertIsNone(obj._metadata)
        self.assertFalse(obj.has_metadata())
        del obj.metadata
        self.assertIsNone(obj._metadata)
        self.assertFalse(obj.has_metadata())

    def test_has_metadata(self):
        obj = self._metadata_constructor_()

        self.assertFalse(obj.has_metadata())
        # Handles metadata efficiently.
        self.assertIsNone(obj._metadata)

        self.assertFalse(
                self._metadata_constructor_(metadata={}).has_metadata())

        self.assertTrue(
                self._metadata_constructor_(metadata={'': ''}).has_metadata())
        self.assertTrue(
                self._metadata_constructor_(
                        metadata={'foo': 42}).has_metadata())


class PositionalMetadataMixinTests:
    def test_constructor_invalid_positional_metadata_type(self):
        with self.assertRaisesRegex(TypeError,
                                    'Invalid positional metadata. Must be '
                                    'consumable by `pd.DataFrame` constructor.'
                                    ' Original pandas error message: '):
            self._positional_metadata_constructor_(0, positional_metadata=2)

    def test_constructor_positional_metadata_len_mismatch(self):
        # Zero elements.
        with self.assertRaisesRegex(ValueError, '\(0\).*\(4\)'):
            self._positional_metadata_constructor_(4, positional_metadata=[])

        # Not enough elements.
        with self.assertRaisesRegex(ValueError, '\(3\).*\(4\)'):
            self._positional_metadata_constructor_(
                4, positional_metadata=[2, 3, 4])

        # Too many elements.
        with self.assertRaisesRegex(ValueError, '\(5\).*\(4\)'):
            self._positional_metadata_constructor_(
                4, positional_metadata=[2, 3, 4, 5, 6])

        # Series not enough rows.
        with self.assertRaisesRegex(ValueError, '\(3\).*\(4\)'):
            self._positional_metadata_constructor_(
                4, positional_metadata=pd.Series(range(3)))

        # Series too many rows.
        with self.assertRaisesRegex(ValueError, '\(5\).*\(4\)'):
            self._positional_metadata_constructor_(
                4, positional_metadata=pd.Series(range(5)))

        # DataFrame not enough rows.
        with self.assertRaisesRegex(ValueError, '\(3\).*\(4\)'):
            self._positional_metadata_constructor_(
                4, positional_metadata=pd.DataFrame({'quality': range(3)}))

        # DataFrame too many rows.
        with self.assertRaisesRegex(ValueError, '\(5\).*\(4\)'):
            self._positional_metadata_constructor_(
                4, positional_metadata=pd.DataFrame({'quality': range(5)}))

    def test_constructor_no_positional_metadata(self):
        # Length zero with missing/empty positional metadata.
        for empty in None, {}, pd.DataFrame():
            obj = self._positional_metadata_constructor_(
                0, positional_metadata=empty)

            self.assertFalse(obj.has_positional_metadata())
            assert_data_frame_almost_equal(obj.positional_metadata,
                                           pd.DataFrame(index=np.arange(0)))

        # Nonzero length with missing positional metadata.
        obj = self._positional_metadata_constructor_(
            3, positional_metadata=None)

        self.assertFalse(obj.has_positional_metadata())
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame(index=np.arange(3)))

    def test_constructor_with_positional_metadata_len_zero(self):
        for data in [], (), np.array([]):
            obj = self._positional_metadata_constructor_(
                0, positional_metadata={'foo': data})

            self.assertTrue(obj.has_positional_metadata())
            assert_data_frame_almost_equal(
                obj.positional_metadata,
                pd.DataFrame({'foo': data}, index=np.arange(0)))

    def test_constructor_with_positional_metadata_len_one(self):
        for data in [2], (2, ), np.array([2]):
            obj = self._positional_metadata_constructor_(
                1, positional_metadata={'foo': data})

            self.assertTrue(obj.has_positional_metadata())
            assert_data_frame_almost_equal(
                obj.positional_metadata,
                pd.DataFrame({'foo': data}, index=np.arange(1)))

    def test_constructor_with_positional_metadata_len_greater_than_one(self):
        for data in ([0, 42, 42, 1, 0, 8, 100, 0, 0],
                     (0, 42, 42, 1, 0, 8, 100, 0, 0),
                     np.array([0, 42, 42, 1, 0, 8, 100, 0, 0])):
            obj = self._positional_metadata_constructor_(
                9, positional_metadata={'foo': data})

            self.assertTrue(obj.has_positional_metadata())
            assert_data_frame_almost_equal(
                obj.positional_metadata,
                pd.DataFrame({'foo': data}, index=np.arange(9)))

    def test_constructor_with_positional_metadata_multiple_columns(self):
        obj = self._positional_metadata_constructor_(
            5, positional_metadata={'foo': np.arange(5),
                                    'bar': np.arange(5)[::-1]})

        self.assertTrue(obj.has_positional_metadata())
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': np.arange(5),
                          'bar': np.arange(5)[::-1]}, index=np.arange(5)))

    def test_constructor_with_positional_metadata_custom_index(self):
        df = pd.DataFrame({'foo': np.arange(5), 'bar': np.arange(5)[::-1]},
                          index=['a', 'b', 'c', 'd', 'e'])
        obj = self._positional_metadata_constructor_(
            5, positional_metadata=df)

        self.assertTrue(obj.has_positional_metadata())
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': np.arange(5),
                          'bar': np.arange(5)[::-1]}, index=np.arange(5)))

    def test_constructor_handles_missing_positional_metadata_efficiently(self):
        obj = self._positional_metadata_constructor_(4)
        self.assertIsNone(obj._positional_metadata)

        obj = self._positional_metadata_constructor_(
            4, positional_metadata=None)
        self.assertIsNone(obj._positional_metadata)

    def test_constructor_makes_shallow_copy_of_positional_metadata(self):
        df = pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                          index=['a', 'b', 'c'])
        obj = self._positional_metadata_constructor_(
            3, positional_metadata=df)

        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                         index=np.arange(3)))
        self.assertIsNot(obj.positional_metadata, df)

        # Original df is not mutated.
        orig_df = pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                               index=['a', 'b', 'c'])
        assert_data_frame_almost_equal(df, orig_df)

        # Change values of column (using same dtype).
        df['foo'] = [42, 42, 42]
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                         index=np.arange(3)))

        # Change single value of underlying data.
        df.values[0][0] = 10
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                         index=np.arange(3)))

        # Mutate list (not a deep copy).
        df['bar'][0].append(42)
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[42], [], []]},
                         index=np.arange(3)))

    def test_eq_basic(self):
        obj1 = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 3]})
        obj2 = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 3]})
        self.assertReallyEqual(obj1, obj2)

    def test_eq_from_different_source(self):
        obj1 = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': np.array([1, 2, 3])})
        obj2 = self._positional_metadata_constructor_(
            3, positional_metadata=pd.DataFrame({'foo': [1, 2, 3]},
                                                index=['foo', 'bar', 'baz']))
        self.assertReallyEqual(obj1, obj2)

    def test_eq_missing_positional_metadata(self):
        for empty in None, {}, pd.DataFrame(), pd.DataFrame(index=[]):
            obj = self._positional_metadata_constructor_(
                0, positional_metadata=empty)

            self.assertReallyEqual(
                obj,
                self._positional_metadata_constructor_(0))
            self.assertReallyEqual(
                obj,
                self._positional_metadata_constructor_(
                    0, positional_metadata=empty))

        for empty in None, pd.DataFrame(index=['a', 'b']):
            obj = self._positional_metadata_constructor_(
                2, positional_metadata=empty)

            self.assertReallyEqual(
                obj,
                self._positional_metadata_constructor_(2))
            self.assertReallyEqual(
                obj,
                self._positional_metadata_constructor_(
                    2, positional_metadata=empty))

    def test_eq_handles_missing_positional_metadata_efficiently(self):
        obj1 = self._positional_metadata_constructor_(1)
        obj2 = self._positional_metadata_constructor_(1)
        self.assertReallyEqual(obj1, obj2)

        self.assertIsNone(obj1._positional_metadata)
        self.assertIsNone(obj2._positional_metadata)

    def test_ne_len_zero(self):
        # Both have positional metadata.
        obj1 = self._positional_metadata_constructor_(
            0, positional_metadata={'foo': []})
        obj2 = self._positional_metadata_constructor_(
            0, positional_metadata={'foo': [], 'bar': []})
        self.assertReallyNotEqual(obj1, obj2)

        # One has positional metadata.
        obj1 = self._positional_metadata_constructor_(
            0, positional_metadata={'foo': []})
        obj2 = self._positional_metadata_constructor_(0)
        self.assertReallyNotEqual(obj1, obj2)

    def test_ne_len_greater_than_zero(self):
        # Both have positional metadata.
        obj1 = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 3]})
        obj2 = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 2]})
        self.assertReallyNotEqual(obj1, obj2)

        # One has positional metadata.
        obj1 = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 3]})
        obj2 = self._positional_metadata_constructor_(3)
        self.assertReallyNotEqual(obj1, obj2)

    def test_copy_positional_metadata_none(self):
        obj = self._positional_metadata_constructor_(3)
        obj_copy = copy.copy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNone(obj._positional_metadata)
        self.assertIsNone(obj_copy._positional_metadata)

    def test_copy_positional_metadata_empty(self):
        obj = self._positional_metadata_constructor_(
            3, positional_metadata=pd.DataFrame(index=range(3)))
        obj_copy = copy.copy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        assert_data_frame_almost_equal(obj._positional_metadata,
                                       pd.DataFrame(index=range(3)))
        self.assertIsNone(obj_copy._positional_metadata)

    def test_copy_with_positional_metadata(self):
        obj = self._positional_metadata_constructor_(
            4, positional_metadata={'bar': [[], [], [], []],
                                    'baz': [42, 42, 42, 42]})
        obj_copy = copy.copy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNot(obj._positional_metadata,
                         obj_copy._positional_metadata)
        self.assertIsNot(obj._positional_metadata.values,
                         obj_copy._positional_metadata.values)
        self.assertIs(obj._positional_metadata.loc[0, 'bar'],
                      obj_copy._positional_metadata.loc[0, 'bar'])

        obj_copy.positional_metadata.loc[0, 'bar'].append(1)
        obj_copy.positional_metadata.loc[0, 'baz'] = 43

        assert_data_frame_almost_equal(
            obj_copy.positional_metadata,
            pd.DataFrame({'bar': [[1], [], [], []],
                          'baz': [43, 42, 42, 42]}))
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'bar': [[1], [], [], []],
                          'baz': [42, 42, 42, 42]}))

    def test_deepcopy_positional_metadata_none(self):
        obj = self._positional_metadata_constructor_(3)
        obj_copy = copy.deepcopy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNone(obj._positional_metadata)
        self.assertIsNone(obj_copy._positional_metadata)

    def test_deepcopy_positional_metadata_empty(self):
        obj = self._positional_metadata_constructor_(
            3, positional_metadata=pd.DataFrame(index=range(3)))
        obj_copy = copy.deepcopy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        assert_data_frame_almost_equal(obj._positional_metadata,
                                       pd.DataFrame(index=range(3)))
        self.assertIsNone(obj_copy._positional_metadata)

    def test_deepcopy_with_positional_metadata(self):
        obj = self._positional_metadata_constructor_(
            4, positional_metadata={'bar': [[], [], [], []],
                                    'baz': [42, 42, 42, 42]})
        obj_copy = copy.deepcopy(obj)

        self.assertEqual(obj, obj_copy)
        self.assertIsNot(obj, obj_copy)

        self.assertIsNot(obj._positional_metadata,
                         obj_copy._positional_metadata)
        self.assertIsNot(obj._positional_metadata.values,
                         obj_copy._positional_metadata.values)
        self.assertIsNot(obj._positional_metadata.loc[0, 'bar'],
                         obj_copy._positional_metadata.loc[0, 'bar'])

        obj_copy.positional_metadata.loc[0, 'bar'].append(1)
        obj_copy.positional_metadata.loc[0, 'baz'] = 43

        assert_data_frame_almost_equal(
            obj_copy.positional_metadata,
            pd.DataFrame({'bar': [[1], [], [], []],
                          'baz': [43, 42, 42, 42]}))
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'bar': [[], [], [], []],
                          'baz': [42, 42, 42, 42]}))

    def test_deepcopy_memo_is_respected(self):
        # Basic test to ensure deepcopy's memo is passed through to recursive
        # deepcopy calls.
        obj = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 3]})
        memo = {}
        copy.deepcopy(obj, memo)
        self.assertGreater(len(memo), 2)

    def test_positional_metadata_getter(self):
        obj = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [22, 22, 0]})

        self.assertIsInstance(obj.positional_metadata, pd.DataFrame)
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [22, 22, 0]}))

        # Update existing column.
        obj.positional_metadata['foo'] = [42, 42, 43]
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [42, 42, 43]}))

        # Add new column.
        obj.positional_metadata['foo2'] = [True, False, True]
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [42, 42, 43],
                          'foo2': [True, False, True]}))

    def test_positional_metadata_getter_no_positional_metadata(self):
        obj = self._positional_metadata_constructor_(4)

        self.assertIsNone(obj._positional_metadata)
        self.assertIsInstance(obj.positional_metadata, pd.DataFrame)
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame(index=np.arange(4)))
        self.assertIsNotNone(obj._positional_metadata)

    def test_positional_metadata_getter_set_column_series(self):
        length = 8
        obj = self._positional_metadata_constructor_(
            length, positional_metadata={'foo': range(length)})

        obj.positional_metadata['bar'] = pd.Series(range(length-3))
        # pandas.Series will be padded with NaN if too short.
        npt.assert_equal(obj.positional_metadata['bar'],
                         np.array(list(range(length-3)) + [np.nan]*3))

        obj.positional_metadata['baz'] = pd.Series(range(length+3))
        # pandas.Series will be truncated if too long.
        npt.assert_equal(obj.positional_metadata['baz'],
                         np.array(range(length)))

    def test_positional_metadata_getter_set_column_array(self):
        length = 8
        obj = self._positional_metadata_constructor_(
            length, positional_metadata={'foo': range(length)})

        # array-like objects will fail if wrong size.
        for array_like in (np.array(range(length-1)), range(length-1),
                           np.array(range(length+1)), range(length+1)):
            with self.assertRaisesRegex(ValueError,
                                        "Length of values does not match "
                                        "length of index"):
                obj.positional_metadata['bar'] = array_like

    def test_positional_metadata_setter_pandas_consumable(self):
        obj = self._positional_metadata_constructor_(3)

        self.assertFalse(obj.has_positional_metadata())

        obj.positional_metadata = {'foo': [3, 2, 1]}
        self.assertTrue(obj.has_positional_metadata())
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [3, 2, 1]}))

        obj.positional_metadata = pd.DataFrame(index=np.arange(3))
        self.assertFalse(obj.has_positional_metadata())
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame(index=np.arange(3)))

    def test_positional_metadata_setter_data_frame(self):
        obj = self._positional_metadata_constructor_(3)

        self.assertFalse(obj.has_positional_metadata())

        obj.positional_metadata = pd.DataFrame({'foo': [3, 2, 1]},
                                               index=['a', 'b', 'c'])
        self.assertTrue(obj.has_positional_metadata())
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [3, 2, 1]}))

        obj.positional_metadata = pd.DataFrame(index=np.arange(3))
        self.assertFalse(obj.has_positional_metadata())
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame(index=np.arange(3)))

    def test_positional_metadata_setter_none(self):
        obj = self._positional_metadata_constructor_(
            0, positional_metadata={'foo': []})

        self.assertTrue(obj.has_positional_metadata())
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': []}))

        # `None` behavior differs from constructor.
        obj.positional_metadata = None

        self.assertFalse(obj.has_positional_metadata())
        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame(index=np.arange(0)))

    def test_positional_metadata_setter_makes_shallow_copy(self):
        obj = self._positional_metadata_constructor_(3)

        df = pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                          index=['a', 'b', 'c'])
        obj.positional_metadata = df

        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                         index=np.arange(3)))
        self.assertIsNot(obj.positional_metadata, df)

        # Original df is not mutated.
        orig_df = pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                               index=['a', 'b', 'c'])
        assert_data_frame_almost_equal(df, orig_df)

        # Change values of column (using same dtype).
        df['foo'] = [42, 42, 42]
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                         index=np.arange(3)))

        # Change single value of underlying data.
        df.values[0][0] = 10
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[], [], []]},
                         index=np.arange(3)))

        # Mutate list (not a deep copy).
        df['bar'][0].append(42)
        assert_data_frame_almost_equal(
            obj.positional_metadata,
            pd.DataFrame({'foo': [22, 22, 0], 'bar': [[42], [], []]},
                         index=np.arange(3)))

    def test_positional_metadata_setter_invalid_type(self):
        obj = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 42]})

        with self.assertRaisesRegex(TypeError,
                                    'Invalid positional metadata. Must be '
                                    'consumable by `pd.DataFrame` constructor.'
                                    ' Original pandas error message: '):
            obj.positional_metadata = 2

        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [1, 2, 42]}))

    def test_positional_metadata_setter_len_mismatch(self):
        obj = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 42]})

        # `None` behavior differs from constructor.
        with self.assertRaisesRegex(ValueError, '\(0\).*\(3\)'):
            obj.positional_metadata = None

        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [1, 2, 42]}))

        with self.assertRaisesRegex(ValueError, '\(4\).*\(3\)'):
            obj.positional_metadata = [1, 2, 3, 4]

        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [1, 2, 42]}))

    def test_positional_metadata_deleter(self):
        obj = self._positional_metadata_constructor_(
            3, positional_metadata={'foo': [1, 2, 3]})

        assert_data_frame_almost_equal(obj.positional_metadata,
                                       pd.DataFrame({'foo': [1, 2, 3]}))

        del obj.positional_metadata
        self.assertIsNone(obj._positional_metadata)
        self.assertFalse(obj.has_positional_metadata())

        # Delete again.
        del obj.positional_metadata
        self.assertIsNone(obj._positional_metadata)
        self.assertFalse(obj.has_positional_metadata())

        obj = self._positional_metadata_constructor_(3)

        self.assertIsNone(obj._positional_metadata)
        self.assertFalse(obj.has_positional_metadata())
        del obj.positional_metadata
        self.assertIsNone(obj._positional_metadata)
        self.assertFalse(obj.has_positional_metadata())

    def test_has_positional_metadata(self):
        obj = self._positional_metadata_constructor_(4)
        self.assertFalse(obj.has_positional_metadata())
        self.assertIsNone(obj._positional_metadata)

        obj = self._positional_metadata_constructor_(0, positional_metadata={})
        self.assertFalse(obj.has_positional_metadata())

        obj = self._positional_metadata_constructor_(
            4, positional_metadata=pd.DataFrame(index=np.arange(4)))
        self.assertFalse(obj.has_positional_metadata())

        obj = self._positional_metadata_constructor_(
            4, positional_metadata=pd.DataFrame(index=['a', 'b', 'c', 'd']))
        self.assertFalse(obj.has_positional_metadata())

        obj = self._positional_metadata_constructor_(
            0, positional_metadata={'foo': []})
        self.assertTrue(obj.has_positional_metadata())

        obj = self._positional_metadata_constructor_(
            4, positional_metadata={'foo': [1, 2, 3, 4]})
        self.assertTrue(obj.has_positional_metadata())

        obj = self._positional_metadata_constructor_(
            2, positional_metadata={'foo': [1, 2], 'bar': ['abc', 'def']})
        self.assertTrue(obj.has_positional_metadata())