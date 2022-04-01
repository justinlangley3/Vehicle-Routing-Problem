from __future__ import annotations

# STL Imports
import inspect
from typing import Generic, Optional, TypeVar

# Project Imports
from .linkedlist import LinkedList, Node
from ..util import debug

Key = TypeVar('Key')
Value = TypeVar('Value')


class HashTable(Generic[Key, Value]):
    _storage = list[LinkedList[tuple[Key, Value]]]
    _buckets = int
    _keys = int

    def __init__(self, buckets=2):
        self._keys: int = 0
        self._buckets: int = buckets
        self._storage: list[LinkedList[tuple[Key, Value]]] = [LinkedList() for _ in range(self._buckets)]

    def __getitem__(self, key: Key) -> Value | None:
        """
        Implements retrieving an item when provided a key
        ex: hashtable[key] returns value
        """
        if key is None:
            raise ValueError(debug.debug_msg(debug.Error.VALUE, inspect.currentframe()))
        b = self._hash(key)
        return self._search_bucket(b, key)

    def __setitem__(self, key: Key, value: Value):
        """
        Implements setting/adding an item as a key, value pair
        ex: hashtable[key] = value
        """
        # a key shouldn't be a null value, even though Python can hash null values
        # i.e. we don't want empty data to make a mess of our HashTable
        if key is None:
            raise ValueError(debug.debug_msg(debug.Error.VALUE, inspect.currentframe()))

        # check if a resize is required
        if self._keys >= (8 * self._buckets):
            self._resize(2 * self._buckets)

        # locate appropriate bucket
        b = self._hash(key)
        self._storage[b].prepend((key, value))
        self._keys += 1

    def __delitem__(self, key):
        """
        Implements deleting an item with the del keyword
        ex: del hashtable[key]
        """
        if key is None:
            raise ValueError(debug.debug_msg(debug.Error.VALUE, inspect.currentframe()))

        b = self._hash(key)
        value: Value = self._search_bucket(b, key)
        is_removed = self._storage[b].remove((key, value))
        try:
            assert is_removed is True
            self._keys -= 1

            if self._buckets > 4 and self._keys <= (2 * self._buckets):
                self._resize(int(0.5 * self._buckets))
        except AssertionError:
            # TODO: Implement error logging
            debug.debug_msg(debug.Error.INDEX, inspect.currentframe())
            return

    def __len__(self):
        return self._keys

    def __iter__(self):
        """
        Allows iterating through items in the hashtable
        Yields key, value pairs as tuples
        """
        for bucket in self._storage:
            for node in bucket:
                data: tuple[Key, Value] = node.data
                key, value = data[0], data[1]
                yield value

    def __next__(self):
        pass

    def __repr__(self):
        return 'HashTable('.join([''.join(f'{bucket})\n') for bucket in self._storage]) + ')'

    def __str__(self):
        return 'HashTable('.join([''.join(f'{bucket})\n') for bucket in self._storage]) + ')'

    def search(self, key: Key) -> bool:
        if key is None:
            raise ValueError(debug.debug_msg(debug.Error.VALUE, inspect.currentframe()))

        b = self._hash(key)
        if self._search_bucket(b, key):
            return True
        return False

    def clear(self) -> None:
        self._keys = 0
        for bucket in self._storage:
            bucket.clear()
        self._resize(new_size=2)

    def items(self):
        """
        Allows iterating through items in the hashtable
        Yields key, value pairs as tuples
        """
        for bucket in self._storage:
            for node in bucket:
                data: tuple[Key, Value] = node.data
                key, value = data[0], data[1]
                yield key, value

    def _hash(self, key: Key) -> int:
        if type(key) is int:
            return key % self._buckets
        return hash(key) % self._buckets

    def _resize(self, new_size: int) -> None:
        # new/old sizes
        old_size = len(self._storage)
        self._buckets = new_size

        # if the table is already empty, ensure no excess storage remains
        if self._is_empty():
            del self._storage[new_size:]
            return

        # add new buckets, if the table is growing
        if new_size > old_size:
            self._storage.extend([LinkedList[tuple[Key, Value]]() for _ in range(new_size - old_size)])

        # iterate previous buckets
        for i in range(old_size):

            # rehash every item stored
            for node in self._storage[i]:
                if node is not Node[None]:
                    key, value = tuple(node.data)[0], tuple(node.data)[1]
                    b = self._hash(key)
                    self._storage[i].remove(node)
                    self._storage[b].prepend((key, value))

        # remove empty buckets, if the table is shrinking
        if new_size < old_size:
            del self._storage[new_size:]

    def _is_empty(self) -> bool:
        return True if self._keys <= 0 else False

    def _search_bucket(self, i: int, k: Key) -> Optional[Value]:
        for node in self._storage[i]:
            node_key, node_val = tuple(node.data)[0], tuple(node.data)[1]
            if node_key == k:
                return node_val
        return None
