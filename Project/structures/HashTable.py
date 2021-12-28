import random
import sys

from . import LinkedList


class HashTable:

    def __init__(self, size: int = 4):
        self.n = 0  # number of (key, val) pairs stored
        self.m = size  # number of 'buckets' i.e. the table size, default is 4
        self.table = [LinkedList.LinkedList() for _ in range(size)]

    def __str__(self):
        return ''.join(str(x) for x in self.table)

    def _bucket(self, key):
        return key % self.m

    def insert(self, key, value: any):
        # check if resize is needed
        if self.n >= (8 * self.m):
            self._resize(2 * self.m)

        b = self._bucket(key)
        self.table[b].push(key, value)
        self.n += 1
        return

    def search(self, key):
        # check if key is contained in the table
        if key < 0 or key > self.n:
            return None

        b = self._bucket(key)
        return self.table[b].search(key)

    def remove(self, key):
        # check if key is contained in the table
        if key < 0 or key > self.n:
            return False

        b = self._bucket(key)
        deleted = self.table[b].remove(key)
        if deleted:
            self.n -= 1

        # check if resizing is needed
        if self.m > 4 and self.n <= 2 * self.m:
            self._resize(int(self.m * 0.5))

        return True

    def _resize(self, s: int):
        """
        Resizes the HashTable in-place.
        Time Complexity - O(n+m), n = total keys, m = buckets to (add/remove)
        :param s:
        :return:
        """
        old_s = len(self.table)
        self.m = s

        if s > old_s:  # Add new buckets, if needed
            self.table.extend([LinkedList.LinkedList() for _ in range(s - old_s)])

        # iterate buckets
        for i in range(old_s):
            node = self.table[i].head
            # traverse the LinkedList
            while node:
                # check if hash is invalid
                if i != self._bucket(node.key):
                    # retain (key, val)
                    k, v = node.key, node.data
                    # remove (key, val) from current bucket
                    self.table[i].remove(node.key)
                    # place  (key, val) in correct bucket
                    self.table[self._bucket(k)].push(k, v)
                node = node.next

        if s < old_s:   # Remove empty buckets, if needed
            del self.table[s:]
