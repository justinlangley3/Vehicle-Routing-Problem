import math
from . import LinkedList


class HashTable:
    def __init__(self, capacity: int = 10):
        self.buckets = 1 if capacity == 1 else nearest_prime(int(8 * capacity / math.log(capacity)))
        self.table = [LinkedList.LinkedList() for i in range(self.buckets)]

    def __str__(self):
        return ''.join(str(x) for x in self.table)

    def insert(self, key, data):
        bucket = key % len(self.table)
        self.table[bucket].push(key, data)
        return

    def search(self, key):
        bucket = key % len(self.table)
        return self.table[bucket].search(key)

    def remove(self, key):
        bucket = key % len(self.table)
        self.table[bucket].remove(key)


def is_prime(p):
    # test if a number(p) is prime by checking in the range: 0 to sqrt(p) + 1 for factors
    for i in range(2, int(pow(p, 1 / 2) + 1)):
        if p % i == 0:
            return False
    return True


def nearest_prime(p):
    if is_prime(p):
        return p
    # test for nearest prime at or below p
    for i in range(p)[::-1]:
        if is_prime(i):
            return i
