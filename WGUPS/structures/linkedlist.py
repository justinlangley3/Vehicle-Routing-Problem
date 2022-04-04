from __future__ import annotations

# STL Imports
import inspect
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import Generic, TypeVar

# Package Imports
from WGUPS.util import debug

T = TypeVar('T')


@dataclass(eq=True, order=True, unsafe_hash=True)
class Node(Generic[T]):
    data: T
    next: Node = None
    prev: Node = None

    def __repr__(self):
        return f'Node({self.data})'


# noinspection DuplicatedCode
class LinkedList(Generic[T]):
    """
    Doubly-Linked List Implementation
    Big-O for Operations:
    -------------------------------------
    | Access | Search | Insert | Delete |
    | O(n)   | O(n)   | O(1)   | O(1)   |
    -------------------------------------
    """
    # Class vars
    head: Node[T]
    tail: Node[T]
    size: int

    #
    # Magic Methods
    #
    def __init__(self) -> None:
        self.head = Node[None]
        self.tail = Node[None]
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, i: int) -> Node[T]:
        assert self._is_element_index(i)
        count = 0
        if i < (self.size >> 1):
            for node in self:
                if count == i:
                    return node
                i += 1
        else:
            i = self.size - i
            for node in reversed(self):
                if count == i:
                    return node
                i += 1

    def __iter__(self) -> AscendingLinkedListIterator:
        return self.AscendingLinkedListIterator(self.head)

    def __reversed__(self) -> DescendingLinkedListIterator:
        return self.DescendingLinkedListIterator(self.tail)

    def __next__(self):
        pass

    def __repr__(self):
        return 'LinkedList('.join([''.join(f'{node})\n') for node in self]) + ')'

    #
    # Public Methods
    #

    #
    # Get Operations
    def get_first(self) -> Node[T]:
        assert self.head is not None
        return self.head

    def get_last(self) -> Node[T]:
        assert self.tail is not None
        return self.tail

    #
    # Insert Operations
    def append(self, e: T) -> None:
        self._link_last(e)

    def prepend(self, e: T) -> None:
        self._link_first(e)

    #
    # Remove Operations
    def clear(self) -> None:
        for node in self:
            node.data = None
            node.next = None
            node.prev = None
        self.head = Node[None]
        self.tail = self.head
        self.size = 0

    def remove_first(self) -> T:
        h = self.head
        assert h is not None
        return self._unlink_first(h)

    def remove_last(self) -> T:
        t = self.tail
        assert t is not None
        return self._unlink_last(t)

    @singledispatchmethod
    def remove(self, e: T) -> bool:
        if e is None:
            for node in self:
                if node.data is None:
                    self._unlink(node)
                    return True
        else:
            for node in self:
                if node.data is e:
                    self._unlink(node)
                    return True
        return False

    @remove.register
    def _(self, i: int) -> None:
        self._check_element_index(i)
        return self._unlink(self.node(i))

    @remove.register
    def _(self, n: Node) -> None:
        for node in self:
            if n is node:
                return self._unlink(node)

    #
    # Size Operations
    def size(self) -> int:
        return self.size

    def is_empty(self) -> bool:
        return not self.head

    #
    # Conversion
    def to_list(self) -> list[T]:
        return [node.data for node in self]

    #
    # Positional Operations
    def node(self, i: int) -> Node[T]:
        assert self._is_element_index(i)
        count = 0
        if i < (self.size >> 1):
            for n in self:
                if count == i:
                    return n
                i += 1
        else:
            i = self.size - i
            for n in reversed(self):
                if count == i:
                    return n
                i += 1

    #
    # Search Operations
    def index_of(self, e: T) -> int:
        i = 0
        if e is None:
            for node in self:
                if node.data is None:
                    return i
                i += 1
        else:
            for node in self:
                if node is e:
                    return i
                i += 1

    def last_index_of(self, e: T) -> int:
        i = self.size
        if e is None:
            for node in reversed(self):
                i -= 1
                if node.val is None:
                    return i
        else:
            for node in reversed(self):
                i -= 1
                if node.val is e:
                    return i

    #
    # Private methods
    #

    #
    # Positional Operations
    def _is_element_index(self, i: int) -> bool:
        return 0 <= i <= self.size

    def _is_position_index(self, i: int) -> bool:
        return 0 <= i <= self.size

    def _check_element_index(self, i) -> None:
        if not self._is_position_index(i):
            raise IndexError(debug.debug_msg(debug.Error.INDEX, inspect.currentframe()))

    def _check_position_index(self, i) -> None:
        if not self._is_position_index(i):
            raise IndexError(debug.debug_msg(debug.Error.INDEX, inspect.currentframe()))

    #
    # Linking/Unlinking Operations
    def _link_first(self, e: T) -> None:
        head = self.head
        new_node = Node(data=e, next=head, prev=Node[None])
        self.head = new_node
        # pointer adjustments on old head
        if head is None:
            self.tail = new_node
        else:
            head.prev = new_node
        self.size += 1

    def _link_last(self, e: T) -> None:
        tail = self.tail
        new_node = Node(data=e, next=Node[None], prev=tail)
        self.tail = new_node
        # pointer adjustments on old tail
        if tail is None:
            self.head = new_node
        else:
            tail.next = new_node
        self.size += 1

    def _link_before(self, e: T, successor: Node[T]) -> None:
        predecessor = successor.prev
        new_node = Node(data=e, next=successor, prev=predecessor)
        successor.prev = new_node
        if predecessor is None:
            self.head = new_node
        else:
            predecessor.next = new_node
        self.size += 1

    def _unlink_first(self, head: Node[T]) -> T:
        e = head.data
        new_head = head.next
        del head.data, head.next
        self.head = new_head
        # pointer adjustments
        if new_head is None:
            self.tail = Node[None]
        else:
            new_head.prev = Node[None]
        self.size -= 1
        return e

    def _unlink_last(self, tail: Node[T]) -> T:
        e = tail.data
        new_tail = tail.prev
        del tail.data, tail.prev
        self.tail = new_tail
        # pointer adjustments
        if new_tail is None:
            self.head = Node[None]
        else:
            new_tail.next = Node[None]
        self.size -= 1
        return e

    def _unlink(self, n: Node[T]) -> T:
        assert n is not None
        if n is self.head:
            return self._unlink_first(n)
        if n is self.tail:
            return self._unlink_last(n)
        else:
            for node in self:
                if node.next is n:
                    e = node.next.data
                    next_node = n.next
                    prev_node = node
                    # adjust pointers
                    node.next = next_node
                    next_node.prev = prev_node
                    del n
                    self.size -= 1
                    return e
            else:
                raise LookupError(debug.debug_msg(debug.Error.LOOKUP, inspect.currentframe()))

    #
    # Member Classes
    #

    #
    # Iterators
    class AscendingLinkedListIterator:
        def __init__(self, head: Node[T]):
            self._node = head
            self._index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._node is Node[None]:
                raise StopIteration
            else:
                self._index += 1
                item = self._node
                self._node = self._node.next
                return item

    class DescendingLinkedListIterator:
        def __init__(self, tail: Node[T]):
            self._node = tail
            self._index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._node is Node[None]:
                raise StopIteration
            else:
                self._index += 1
                item = self._node
                self._node = self._node.prev
                return item
