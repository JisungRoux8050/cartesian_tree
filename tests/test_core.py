import unittest

from cartesian_tree import CartesianTree, Node, build, build_indexed


class TestBuild(unittest.TestCase):
    def test_empty(self):
        t = build([])
        self.assertIsNone(t.root)
        self.assertEqual(len(t), 0)
        self.assertTrue(t.is_empty())
        self.assertFalse(bool(t))
        self.assertEqual(list(t.values()), [])
        self.assertIsNone(t.min_index())

    def test_single(self):
        t = build([7])
        self.assertIsNotNone(t.root)
        self.assertEqual(t.root.index, 0)
        self.assertEqual(t.root.value, 7)
        self.assertIsNone(t.root.left)
        self.assertIsNone(t.root.right)
        self.assertEqual(len(t), 1)
        self.assertEqual(list(t.values()), [7])
        self.assertEqual(list(t.indices()), [0])

    def test教科书_example(self):
        # Classic textbook example: minimum at index 3 (value 1)
        t = build([9, 3, 7, 1, 8, 12, 10, 0, 14, 4, 2, 5, 11, 6])
        self.assertEqual(t.min_index(), 7)  # value 0 is the minimum
        # In-order must reproduce the input.
        self.assertEqual(list(t.values()),
                         [9, 3, 7, 1, 8, 12, 10, 0, 14, 4, 2, 5, 11, 6])

    def test_in_order_reproduces_input(self):
        cases = [
            [5],
            [1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1],
            [3, 1, 4, 1, 5, 9, 2, 6],
            [0, 0, 0],
            [-1, -3, -2, 0],
        ]
        for arr in cases:
            with self.subTest(arr=arr):
                t = build(arr)
                self.assertEqual(list(t.values()), arr)
                self.assertEqual(list(t.indices()), list(range(len(arr))))

    def test_heap_property_root_min(self):
        t = build([9, 3, 7, 1, 8, 12, 10, 0, 14, 4, 2, 5, 11, 6])
        # Root is the global minimum.
        self.assertEqual(t.root.value, 0)
        # Every child is >= its parent.
        def check(node):
            if node is None:
                return
            if node.left:
                self.assertGreaterEqual(node.left.value, node.value)
                check(node.left)
            if node.right:
                self.assertGreaterEqual(node.right.value, node.value)
                check(node.right)
        check(t.root)

    def test_strictly_increasing_spine(self):
        # Sorted ascending input produces a right-only spine.
        t = build([1, 2, 3, 4, 5])
        node = t.root
        for expected in [1, 2, 3, 4, 5]:
            self.assertIsNotNone(node)
            self.assertEqual(node.value, expected)
            self.assertIsNone(node.left)
            node = node.right

    def test_strictly_decreasing_spine(self):
        # Sorted descending input produces a left-only spine.
        t = build([5, 4, 3, 2, 1])
        node = t.root
        for expected in [1, 2, 3, 4, 5]:
            self.assertIsNotNone(node)
            self.assertEqual(node.value, expected)
            self.assertIsNone(node.right)
            node = node.left

    def test_equal_values_leftmost_wins(self):
        # All equal: root should be index 0, spine to the right.
        t = build([2, 2, 2, 2])
        self.assertEqual(t.root.index, 0)
        self.assertEqual(t.root.value, 2)
        node = t.root
        for expected_idx in [0, 1, 2, 3]:
            self.assertIsNotNone(node)
            self.assertEqual(node.index, expected_idx)
            self.assertIsNone(node.left)
            node = node.right

    def test_negative_and_zero_values(self):
        t = build([-3, 0, -1, 2, -5])
        self.assertEqual(t.root.value, -5)
        self.assertEqual(t.root.index, 4)
        self.assertEqual(list(t.values()), [-3, 0, -1, 2, -5])


class TestBuildIndexed(unittest.TestCase):
    def test_empty_pairs(self):
        t = build_indexed([])
        self.assertIsNone(t.root)
        self.assertEqual(len(t), 0)

    def test_custom_indices_preserved(self):
        pairs = [(10, 5.0), (20, 3.0), (30, 7.0)]
        t = build_indexed(pairs)
        self.assertEqual(t.min_index(), 20)
        # In-order follows pair order, not numeric index order.
        self.assertEqual(list(t.indices()), [10, 20, 30])
        self.assertEqual(list(t.values()), [5.0, 3.0, 7.0])

    def test_custom_indices_unsorted(self):
        pairs = [(7, 1.0), (2, 2.0), (9, 0.5)]
        t = build_indexed(pairs)
        self.assertEqual(t.min_index(), 9)
        self.assertEqual(list(t.indices()), [7, 2, 9])

    def test_float_values(self):
        t = build([1.5, 0.25, 3.0, 0.25])
        self.assertEqual(t.root.value, 0.25)
        self.assertEqual(t.root.index, 1)  # first occurrence of min
        # Second 0.25 attaches as right descendant of the first.
        self.assertEqual(list(t.values()), [1.5, 0.25, 3.0, 0.25])


class TestErrors(unittest.TestCase):
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            build([1.0, float("nan"), 2.0])

    def test_bool_rejected(self):
        with self.assertRaises(TypeError):
            build([True, False])

    def test_string_value_rejected(self):
        with self.assertRaises(TypeError):
            build(["a", "b"])

    def test_non_int_index_rejected(self):
        with self.assertRaises(TypeError):
            build_indexed([(1.5, 2.0)])

    def test_bool_index_rejected(self):
        with self.assertRaises(TypeError):
            build_indexed([(True, 2.0)])


class TestCartesianTreeAPI(unittest.TestCase):
    def test_equality_by_values(self):
        a = build([3, 1, 2])
        b = build([3, 1, 2])
        self.assertEqual(a, b)
        c = build([3, 1, 4])
        self.assertNotEqual(a, c)

    def test_equality_with_non_tree(self):
        t = build([1, 2])
        self.assertFalse(t == [1, 2])
        self.assertTrue(t != [1, 2])

    def test_repr_empty(self):
        t = build([])
        r = repr(t)
        self.assertIn("empty", r)

    def test_repr_nonempty(self):
        t = build([3, 1, 2])
        r = repr(t)
        self.assertIn("root_index=1", r)
        self.assertIn("size=3", r)

    def test_iter_yields_nodes_in_order(self):
        t = build([5, 3, 4])
        nodes = list(t)
        self.assertEqual(len(nodes), 3)
        self.assertEqual([n.value for n in nodes], [5, 3, 4])
        for n in nodes:
            self.assertIsInstance(n, Node)

    def test_min_index_single(self):
        t = build([42])
        self.assertEqual(t.min_index(), 0)


class TestNode(unittest.TestCase):
    def test_repr_leaf(self):
        n = Node(0, 1.0)
        self.assertIn("leaf", repr(n))

    def test_repr_left_only(self):
        n = Node(0, 1.0, left=Node(1, 2.0))
        self.assertIn("left", repr(n))

    def test_repr_right_only(self):
        n = Node(0, 1.0, right=Node(1, 2.0))
        self.assertIn("right", repr(n))

    def test_repr_two_children(self):
        n = Node(0, 1.0, Node(1, 2.0), Node(2, 3.0))
        self.assertIn("two", repr(n))

    def test_in_order_empty_subtree(self):
        # A leaf node's in_order yields just itself.
        n = Node(0, 5.0)
        self.assertEqual([x.value for x in n.in_order()], [5.0])


if __name__ == "__main__":
    unittest.main()
