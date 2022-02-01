import pytest
import operator
import unittest
from numpy.testing import assert_array_equal
from dnplab.core.base import ABCData
from dnplab.core.coord import nddata_coord_collection, nddata_coord
import numpy as np
import random

from dnplab.core.coord import nddata_coord, nddata_coord_collection

test_dims = ["x", "y", "z", "p", "q", "r"]
num_random_tests = 10


def get_random_ABCData_list(seed_axis=0, seed_data=0):
    """
    Pre-generate a list of randomized tuple (ABCData, np.array) for all the
    test cases here
    """
    random.seed(seed_axis)
    random_axes = [
        random.sample(
            list(zip(test_dims, [np.r_[0 : random.randint(1, 6)] for _ in test_dims])),
            3,
        )
        for _ in range(3)
    ]
    random.seed(seed_data)
    ABCData_list = []
    for random_axis in random_axes:
        dims = [axis[0] for axis in random_axis]
        coords = [axis[1] for axis in random_axis]
        shape = [coord.size for coord in coords]
        values = np.random.randn(*shape)
        ABCData_list.append((ABCData(values, dims, coords), values))
    # ABCData_list.append((ABCData.ABCData_core(), np.array([])))  # UserWarning: Github #37
    return ABCData_list


random_ABCData_list = get_random_ABCData_list(seed_axis=0, seed_data=0)
random_ABCData_list_2 = get_random_ABCData_list(seed_axis=0, seed_data=1)


@pytest.mark.filterwarnings("ignore:divide by zero")
# See https://docs.python.org/3/library/operator.html#mapping-operators-to-functions
@pytest.mark.parametrize(
    "operator", [operator.add, operator.sub, operator.mul, operator.truediv]
)
@pytest.mark.parametrize("ABCData_value_tuple", random_ABCData_list)
@pytest.mark.parametrize("number", [-1.1j, -1.1, -1, 0, 1, 1.1, 1.1j])
def test_ABCData_core_math_operators_numeric(operator, ABCData_value_tuple, number):
    ABCData, values = ABCData_value_tuple
    assert_array_equal(operator(ABCData, number).values, operator(values, number))
    assert_array_equal(operator(number, ABCData).values, operator(number, values))


@pytest.mark.parametrize(
    "operator", [operator.add, operator.sub, operator.mul, operator.truediv]
)
@pytest.mark.parametrize("i_data", range(0, len(random_ABCData_list)))
def test_ABCData_core_math_operators(operator, i_data):
    ABCData, values = random_ABCData_list[i_data]
    ABCData_2, values_2 = random_ABCData_list_2[i_data]
    ABCData_3, values_3 = operator(ABCData, ABCData_2), operator(values, values_2)
    # assert self consistent
    assert ABCData_3._self_consistent()
    # assert values equal
    assert_array_equal(ABCData_3.values, values_3)


def test_ABCData_core_math_div_by_zero():
    with pytest.warns(RuntimeWarning):
        ABCData(
            values=np.array([1, 2, 3]), coords=[np.array([3, 2, 1])], dims=["x"]
        ) / 0


class dnplab_ABCData_core_tester(unittest.TestCase):
    def setUp(self):
        self.dims = test_dims
        random.sample(test_dims, random.randint(1, len(test_dims)))

    def construct_random_data(self):
        random_dims = random.sample(test_dims, random.randint(1, len(test_dims)))

        random_coords = [np.r_[0 : random.randint(1, 6)] for dim in random_dims]
        shape = [coord.size for coord in random_coords]

        random_values = np.random.randn(*shape)
        data = ABCData(random_values, random_dims, random_coords)
        return data, random_dims, random_values, random_coords

    def test_ABCData_core_init(self):
        for ix in range(num_random_tests):
            (
                data,
                random_dims,
                random_values,
                random_coords,
            ) = self.construct_random_data()
            self.assertTrue(data._self_consistent())
            assert_array_equal(data.values, random_values)
            for ix, dim in enumerate(random_dims):
                assert_array_equal(data.coords[dim], random_coords[ix])
            self.assertListEqual(data.dims, random_dims)

    def test_coord_type(self):
        data, _, _, _ = self.construct_random_data()
        self.assertEqual(type(data.coords), nddata_coord_collection)

    def test_ndim(self):
        values = np.r_[1:10].reshape(3, 3)
        x = np.r_[0:3]
        y = np.r_[0:3]

        data = ABCData(values, ["x", "y"], [x, y])

        self.assertEqual(data.ndim, 2)


class dnplab_ABCData_coord_tester(unittest.TestCase):
    def setUp(self):
        self.coord_inst_a = nddata_coord("a", slice(0, 10, 1))
        self.coord_inst_b = nddata_coord("b", slice(0, 1, 50e-3))
        self.numpy_inst = np.r_[1:2:0.25]
        self.collection_inst = nddata_coord_collection(
            ["a", "b", "c"], [self.coord_inst_a, self.coord_inst_b, self.numpy_inst]
        )

    def test_get_str_uses_dim(self):
        assert_array_equal(self.collection_inst.dims, ["a", "b", "c"])

    def test_str_rep(self):
        self.assertEqual(str(self.collection_inst["a"]), r"'a':[0 1 2 3 4 5 6 7 8 9]")

    def test_get_int_uses_index(self):
        assert_array_equal(self.collection_inst[0], self.coord_inst_a)

    def test_like_dict(self):
        assert_array_equal(self.collection_inst["a"], self.coord_inst_a)

    def test_reorder_only_1_dim(self):
        self.collection_inst.reorder(["c"])
        assert_array_equal(self.collection_inst.dims, ["c", "a", "b"])

    def test_reorder_all_3_dims(self):
        self.collection_inst.reorder(["b", "c", "a"])
        assert_array_equal(self.collection_inst.dims, ["b", "c", "a"])

    def test_rename(self):
        self.collection_inst.rename("a", "new_a")
        assert_array_equal(self.collection_inst.dims, ["new_a", "b", "c"])

    def test_rename_child_rep_changes(self):
        self.collection_inst.rename("a", "new_a")
        self.assertEqual(
            str(self.collection_inst["new_a"]), r"'new_a':[0 1 2 3 4 5 6 7 8 9]"
        )
