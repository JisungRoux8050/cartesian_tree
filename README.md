# cartesian_tree

A cartesian tree is a heap-ordered binary tree built from an array: the root is the array's minimum, and an in-order traversal reproduces the original sequence. This library builds one in O(n) and exposes the resulting structure for traversal and root queries.

## Install

`PYTHONPATH=src python -m unittest discover -s tests`

## Usage

```python
from cartesian_tree import build, build_indexed

# Build from a plain value sequence.
t = build([9, 3, 7, 1, 8, 12, 10, 0, 14, 4, 2, 5, 11, 6])
print(t.root.index, t.root.value)   # 7 0
print(list(t.values()))              # original order preserved
print(list(t.indices()))             # 0..13
print(t.min_index())                 # 7

# Build from (index, value) pairs when indices are non-contiguous.
t2 = build_indexed([(10, 5.0), (20, 3.0), (30, 7.0)])
print(t2.min_index())                # 20
print(list(t2.indices()))            # [10, 20, 30]
```

## Why this exists

Cartesian trees give you both a heap view (minimum at the root) and a sequence view (in-order traversal) of the same data, in O(n) build time. They are the backbone of offline range-minimum queries and of the Treap's structural argument. The trade-off: query time on a balanced tree is O(log n), but a sorted input degenerates into a spine and queries become O(n). If you need worst-case O(1) RMQ, use a sparse table instead.

## Decisions and edges

- **Min-heap, not max-heap.** The root is the minimum element. If you need a max-heap, negate your values before building.
- **Tie-break: leftmost wins.** When two equal values appear, the earlier index becomes the ancestor and later equal values descend to its right. This keeps the build fully deterministic.
- **NaN is rejected.** NaN violates total ordering and would silently corrupt the heap invariant.
- **Booleans are rejected as values** to avoid the bool-is-int trap where `True` and `1` compare equal.
- **`build_indexed` in-order follows pair order, not numeric index.** The heap property is only compatible with the in-order property when in-order means sequence order. If you need numeric-index order, sort the pairs first.

## Exports

- `build(values)` → `CartesianTree`
- `build_indexed(pairs)` → `CartesianTree` where `pairs` is a sequence of `(int, float)`
- `CartesianTree` with: `root`, `len()`, `is_empty()`, `__bool__`, `__iter__` (nodes in order), `values()`, `indices()`, `min_index()`, `__eq__`, `__repr__`
- `Node` with: `index`, `value`, `left`, `right`, `in_order()`, `__repr__`
