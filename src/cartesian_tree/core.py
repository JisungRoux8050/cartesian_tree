"""Cartesian tree: a heap-ordered binary tree built from an array.

A cartesian tree over an array A satisfies two invariants:
  - Heap property: parent value <= child values (min-heap).
  - In-order traversal yields the original array order.

The min-heap choice (over max-heap) is a deliberate, documented decision:
min-heap makes the root the minimum element, which matches the most common
use-case (range-minimum queries via the tree's spine). If you need a max-heap,
invert values before building.

For equal values, the leftmost occurrence wins as the root; subsequent equal
values attach as right-spine children. This keeps the in-order invariant intact
and makes the build fully deterministic.
"""

from __future__ import annotations

from typing import Iterator, List, Optional, Sequence, Tuple

__all__ = ["Node", "CartesianTree", "build", "build_indexed"]


class Node:
    """A single node in a cartesian tree.

    Fields are intentionally mutable so callers can rewire a tree by hand.
    For immutable use, don't mutate — copy first.
    """

    __slots__ = ("index", "value", "left", "right")

    def __init__(
        self,
        index: int,
        value: float,
        left: Optional["Node"] = None,
        right: Optional["Node"] = None,
    ) -> None:
        self.index = index
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        side = "leaf"
        if self.left is not None and self.right is not None:
            side = "two"
        elif self.left is not None:
            side = "left"
        elif self.right is not None:
            side = "right"
        return f"Node(index={self.index}, value={self.value!r}, {side})"

    def in_order(self) -> Iterator["Node"]:
        """Yield nodes left-to-right, reproducing the original array order."""
        node = self
        stack: List[Node] = []
        while node is not None or stack:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node
            node = node.right


def _build_spine(seq: Sequence[float]) -> Optional[Node]:
    """Build a cartesian tree from a plain value sequence.

    Uses the classic right-spine stack algorithm: O(n) time, O(height) auxiliary.
    The right spine is maintained as a stack of nodes with strictly increasing
    values. Each new element pops the spine until it finds a strictly-smaller
    parent, takes the last popped subtree as its left child, and attaches as
    that parent's new right child.

    Equality is handled by strict comparison (<), so when a new value equals
    the top of spine, the existing node stays above the new one. This is the
    "leftmost wins" tie-break: the earlier index becomes the ancestor.
    """
    if not seq:
        return None

    stack: List[Node] = []
    for i, v in enumerate(seq):
        node = Node(i, v)
        last_popped: Optional[Node] = None
        while stack and stack[-1].value > v:
            last_popped = stack.pop()
        if last_popped is not None:
            node.left = last_popped
        if stack:
            stack[-1].right = node
        stack.append(node)

    return stack[0] if stack else None


def build(values: Sequence[float]) -> "CartesianTree":
    """Build a cartesian tree from a sequence of values.

    Values are interpreted as floats; non-numeric inputs raise TypeError from
    the comparison itself. NaN values violate total ordering and are explicitly
    rejected to keep the invariants provable.
    """
    for v in values:
        _check_value(v)
    root = _build_spine(values)
    return CartesianTree(root, len(values))


def build_indexed(pairs: Sequence[Tuple[int, float]]) -> "CartesianTree":
    """Build a cartesian tree from (index, value) pairs.

    The ``index`` is whatever integer the caller supplies; it need not match
    position in the sequence, which lets you build trees over sparse or
    non-contiguous indices. The in-order traversal follows the sequence order
    of the pairs, NOT the numeric index field — this is what makes the heap
    property compatible with the in-order property for arbitrary index sets.
    """
    checked: List[Tuple[int, float]] = []
    for idx, v in pairs:
        if not isinstance(idx, int) or isinstance(idx, bool):
            raise TypeError(f"index must be int, got {type(idx).__name__}")
        _check_value(v)
        checked.append((idx, v))

    if not checked:
        return CartesianTree(None, 0)

    stack: List[Node] = []
    for idx, v in checked:
        node = Node(idx, v)
        last_popped: Optional[Node] = None
        while stack and stack[-1].value > v:
            last_popped = stack.pop()
        if last_popped is not None:
            node.left = last_popped
        if stack:
            stack[-1].right = node
        stack.append(node)

    return CartesianTree(stack[0] if stack else None, len(checked))


def _check_value(v: object) -> None:
    """Reject values that would break the total-order invariant."""
    if isinstance(v, bool):
        raise TypeError("booleans are not accepted as values; pass int or float")
    if isinstance(v, (int, float)):
        import math
        if isinstance(v, float) and math.isnan(v):
            raise ValueError("NaN cannot participate in cartesian tree ordering")
        return
    raise TypeError(f"value must be int or float, got {type(v).__name__}")


class CartesianTree:
    """A cartesian tree over a sequence of values.

    Construction is O(n). Query helpers are intentionally minimal: this class
    is a structure, not an RMQ engine. Range-minimum queries can be answered in
    O(log n) expected via subtree bounds, but the worst case is O(n) for a
    sorted input (degenerate spine). If you need guaranteed RMQ, use a
    sparse-table or segment tree instead.
    """

    __slots__ = ("_root", "_size")

    def __init__(self, root: Optional[Node], size: int) -> None:
        self._root = root
        self._size = size

    @property
    def root(self) -> Optional[Node]:
        return self._root

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._root is None

    def __bool__(self) -> bool:
        return self._root is not None

    def __iter__(self) -> Iterator[Node]:
        if self._root is None:
            return iter(())
        return self._root.in_order()

    def values(self) -> Iterator[float]:
        """Yield values in original array order."""
        for node in self:
            yield node.value

    def indices(self) -> Iterator[int]:
        """Yield node indices in original array order."""
        for node in self:
            yield node.index

    def min_index(self) -> Optional[int]:
        """Return the index of the minimum element, or None if empty.

        The root holds the global minimum by the heap property, so this is O(1).
        """
        if self._root is None:
            return None
        return self._root.index

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CartesianTree):
            return NotImplemented
        return list(self.values()) == list(other.values())

    def __hash__(self) -> int:
        return hash(tuple(self.values()))

    def __repr__(self) -> str:
        if self._root is None:
            return f"CartesianTree(empty, size=0)"
        return f"CartesianTree(root_index={self._root.index}, root_value={self._root.value!r}, size={self._size})"
