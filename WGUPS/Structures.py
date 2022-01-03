from __future__ import annotations
import Debug
import inspect
from Debug import debug_msg
from typing import TypeVar, Generic
from functools import singledispatchmethod

T = TypeVar('T')


class Node(Generic[T]):
    # Class vars
    hash: int
    data: T
    prev_ref: Node[T]
    next_ref: Node[T]

    #
    # Magic Methods
    #
    def __init__(self, prev_node: Node[T] = None, key: int = None, data: T = None, next_node: Node[T] = None):
        self.hash = key
        self.data = data
        self.prev_ref = prev_node
        self.next_ref = next_node

    def __getitem__(self, key: int | str) -> Node[T] | int | T | None:
        """
        Allows accessing instance variables by index or name
        :param key: <p>int: -> node[0|1|2|3] = {self.prev, self.key, self.val, self.next}</p>
                    <p>str: -> node['prev_ref'], node['hash'], node['data'], node['next_ref']</p>
        :return: Node[T] | int | T | None
        """
        if isinstance(key, int):
            if 0 < key <= 3:
                if key == 0:
                    return self.prev
                elif key == 1:
                    return self.key
                elif key == 2:
                    return self.val
                else:
                    return self.next
            else:
                raise IndexError(debug_msg(Debug.Error.INDEX, inspect.currentframe()))
        return getattr(self, key)

    # Strings
    def __repr__(self):
        return f'Node(key={repr(self.key)}, val={repr(self.data)})'

    def __str__(self):
        return str(self.data)

    #
    # Comparisons
    def __eq__(self, other):
        assert (isinstance(other, Node)), debug_msg(Debug.Error.TYPE, inspect.currentframe())
        if isinstance(other, Node):
            return self.data == other.data
        return False

    def __ne__(self, other):
        assert (isinstance(other, Node)), debug_msg(Debug.Error.TYPE, inspect.currentframe())
        if isinstance(other, Node):
            return self.data != other.data
        return False

    def __lt__(self, other):
        assert (isinstance(other, Node)), debug_msg(Debug.Error.TYPE, inspect.currentframe())
        if isinstance(other, Node):
            return self.data < other.data
        return False

    def __gt__(self, other):
        assert (isinstance(other, Node)), debug_msg(Debug.Error.TYPE, inspect.currentframe())
        if isinstance(other, Node):
            return self.data > other.data
        return False

    def __le__(self, other):
        assert (isinstance(other, Node)), debug_msg(Debug.Error.TYPE, inspect.currentframe())
        if isinstance(other, Node):
            return self.data <= other.data
        return False

    def __ge__(self, other):
        assert (isinstance(other, Node)), debug_msg(Debug.Error.TYPE, inspect.currentframe())
        if isinstance(other, Node):
            return self.data >= other.data
        return False

    # getter properties
    @property
    def key(self) -> int:
        return self.hash

    @property
    def next(self) -> Node[T]:
        return Node[None] if self.next_ref is None else self.next_ref

    @property
    def prev(self) -> Node[T]:
        return Node[None] if self.prev_ref is None else self.prev_ref

    @property
    def val(self) -> T:
        return self.data

    # setter properties
    @key.setter
    def key(self, i: int) -> None:
        self.hash = i

    @next.setter
    def next(self, o: Node[T]) -> None:
        self.next_ref = o

    @prev.setter
    def prev(self, o: Node[T]) -> None:
        self.prev_ref = o

    @val.setter
    def val(self, e: T) -> None:
        self.data = e

    # deleter properties
    @key.deleter
    def key(self) -> None:
        self.hash = 0

    @next.deleter
    def next(self) -> None:
        self.next_ref = Node[None]

    @prev.deleter
    def prev(self):
        self.prev_ref = Node[None]

    @val.deleter
    def val(self) -> None:
        self.val = None


class LinkedList(Generic[T]):
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
        """
        Returns the number of Nodes contained in the LinkedList.
        :return: int
        """
        return self.size

    def __getitem__(self, i: int) -> Node[T]:
        """
        Retrieves a Node using a specified index.
        Iterates from the front or back depending on which is shorter.
        :param: i: int
        :return: Node[T]
        """
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
        """
        Allows the LinkedList to be iterable
        :return: Node[T]
        """
        return self.AscendingLinkedListIterator(self.head)

    def __reversed__(self) -> DescendingLinkedListIterator:
        """
        Allows the LinkedList to be iterable in reverse
        :return: Node[T]
        """
        return self.DescendingLinkedListIterator(self.tail)

    def __next__(self):
        """
        Override to allow for iterating
        :return:
        """
        pass

    def __repr__(self):
        """
        Generates a containerized representation of the LinkedList object
        :return:
        """
        r = ''
        count = 0
        for node in self:
            if node is None:
                return
            if count == 0:
                r += f'LinkedList(head={repr(node)})'
            else:
                r += ', '.join(f'node={repr(node)}')
            count += 1
        return r

    def __str__(self):
        """
        Generates a string representation of the LinkedList object
        :return:
        """
        return "\n->".join(str(node) for node in self)

    #
    # Public Methods
    #

    #
    # Get Operations
    def get_first(self) -> Node[T]:
        """
        Retrieves the Node at the head of this LinkedList
        :return: Node[T]
        """
        assert self.head is not None
        return self.head

    def get_last(self) -> Node[T]:
        """
        Retrieves the Node at the tail of this LinkedList
        :return: Node[T]
        """
        assert self.tail is not None
        return self.tail

    #
    # Insert Operations
    def append(self, key: int, e: T) -> None:
        """
        Adds a Node containing element — e at the back of this LinkedList
        :param key: int
        :param e: an element of type T
        :return: None
        """
        self._link_last(key, e)

    def prepend(self, key: int, e: T) -> None:
        """
        Inserts a Node containing element — e at the front of this LinkedList
        :param key: int
        :param e: an element of type T
        :return: None
        """
        self._link_first(key, e)

    @singledispatchmethod
    def add_all(self, c: list[list[int, T]]) -> bool:
        return self.add_all(self.size, c)

    @add_all.register
    def _(self, i: int, c: list[list[int, T]]) -> bool:
        self._check_position_index(i)
        num_elements = len(c)
        if num_elements == 0:
            return False
        p, s = Node[None]

        if i == self.size:
            p = self.tail
        else:
            s = self.node(i, False)
            p = s.prev

        for e in c:
            new_node = Node(p, e[0], e[1], None)
            # pointer adjustments
            if p is None:
                self.head = new_node
            else:
                p.next = s
                s.prev = p
        self.size += num_elements

    #
    # Remove Operations
    def clear(self) -> None:
        """
        Clears the LinkedList
        :return:
        """
        for node in self:
            node.val = None
            node.next = None
            node.prev = None
        self.head = Node[None]
        self.tail = self.head
        self.size = 0

    def remove_first(self) -> T:
        """
        Removes the Node at the head of this LinkedList and returns its data
        :return: element of type T
        """
        h = self.head
        assert h is not None
        return self._unlink_first(h)

    def remove_last(self) -> T:
        """
        Removes the Node at the tail of this LinkedList and returns its data
        :return: element of type T
        """
        t = self.tail
        assert t is not None
        return self._unlink_last(t)

    @singledispatchmethod
    def remove(self, e: T) -> bool:
        """
        Removes a node by matching against its contents
        :param e: element of type T
        :return: bool
        """
        if e is None:
            for node in self:
                if node.val is None:
                    self._unlink(node)
                    return True
        else:
            for node in self:
                if node.val is e:
                    self._unlink(node)
                    return True
        return False

    @remove.register
    def _(self, i: int, is_key: bool) -> None:
        """
        <p>If argument: 'is_key': is True, treat 'i' as a key
        \tThe first node containing the matching key is removed.</p>
        <p>If argument: 'is_key': is False, then 'i' is treated as an index
        \tThe node at the index is removed.</p>
        :param i: int
        :param is_key: bool
        :return: None
        """
        if is_key:
            for node in self:
                if node.key == i:
                    return self._unlink(node)
        else:
            self._check_element_index(i)
            return self._unlink(self.node(i, False))

    @remove.register
    def _(self, n: Node) -> None:
        """
        <p>This is a singledispatchmethod that removes the first occurence of a node matching the one provided.</p>
        :param n:
        :return:
        """
        for node in self:
            if n is node:
                return self._unlink(node)

    #
    # Size Operations
    def size(self) -> int:
        """
        Return the current size of this LinkedList
        :return: int
        """
        return self.size

    def is_empty(self) -> bool:
        """
        True if this LinkedList is empty, otherwise, False
        :return: bool
        """
        return not self.head

    #
    # Conversion
    def to_list(self) -> list[tuple[int, T]]:
        """
        Returns a list representation of this LinkedList
        :return: list[tuple[int, T]]
        """
        return [(node.key, node.val) for node in self]

    #
    # Positional Operations
    @singledispatchmethod
    def node(self, i: int) -> Node[T]:
        """
        <p>Returns the node at the provided index, if the index exists</p>
        <p>Additionally, if a second argument of True is provided, i will be treated as a key.</p>
        <p>In this case a singledispatchmethod is called to handle it</p>
        :param i: int
        :return: Node[T]
        """
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

    @node.register
    def _(self, i: int, is_key: bool) -> Node[T]:
        """
        <p>is_key: True - i is treated as a key.
            The corresponding node is searched for and returned</p>
        <p>is_key: False - i is treated as an index.
            self.node(i) is called instead.
            The node at the index is returned</p>
        :param i: int
        :param is_key: bool
        :return: Node[T]
        """
        if is_key:
            for n in self:
                if n.key == i:
                    return n
            else:
                raise LookupError(debug_msg(Debug.Error.LOOKUP, inspect.currentframe()))
        return self.node(i)

    #
    # Search Operations
    def index_of(self, e: T) -> int:
        """
        Returns the index of the Node containing element — e
        :param e: element: T
        :return: int
        """
        i = 0
        if e is None:
            for node in self:
                if node.val is None:
                    return i
                i += 1
        else:
            for node in self:
                if node is e:
                    return i
                i += 1

    def lastIndexOf(self, e: T) -> int:
        """
        Iterates from back to front to determine the last occurrence of an object
        :param e: element: T
        :return: int
        """
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
        """
        Determines if the argument is an index of an existing element
        :param i: int
        :return: bool
        """
        return 0 <= i <= self.size

    def _is_position_index(self, i: int) -> bool:
        """
        Determines if the argument is an indexable position for an iter or add operation
        :param i: int
        :return: bool
        """
        return 0 <= i <= self.size

    def _check_element_index(self, i) -> None:
        """
        Handles raising an Error if the element is not in range
        :param i:
        :return:
        """
        if not self._is_position_index(i):
            raise IndexError(debug_msg(Debug.Error.INDEX, inspect.currentframe()))

    def _check_position_index(self, i) -> None:
        """
        Handles raising an Error if a position is not in range
        :param i:
        :return:
        """
        if not self._is_position_index(i):
            raise IndexError(debug_msg(Debug.Error.INDEX, inspect.currentframe()))

    #
    # Linking/Unlinking Operations
    def _link_first(self, key: int, e: T) -> None:
        """
        Inserts a new Node as the head of this LinkedList
        :param e: element of type T
        :return: None
        """
        head = self.head
        new_node = Node(Node[None], key, e, head)
        self.head = new_node
        # pointer adjustments on old head
        if head is None:
            self.tail = new_node
        else:
            head.prev = new_node
        self.size += 1

    def _link_last(self, key: int, e: T) -> None:
        """
        Add a new Node as the tail of this LinkedList
        :param e: element of type T
        :return: None
        """
        tail = self.tail
        new_node = Node(tail, key, e, None)
        self.tail = new_node
        # pointer adjustments on old tail
        if tail is None:
            self.head = new_node
        else:
            tail.next = new_node
        self.size += 1

    def _link_before(self, key: int, e: T, s: Node[T]) -> None:
        """
        Inserts a new Node before the specified node
        :param e: element of type T
        :param s: the succeeding node
        :return: None
        """
        p = s.prev
        new_node = Node(p, key, e, s)
        s.prev = new_node
        if p is None:
            self.head = new_node
        else:
            p.next = new_node
        self.size += 1

    def _unlink_first(self, head: Node[T]) -> T:
        """
        Unlinks the first Node and returns its data
        :param head: Node[T]
        :return: element of type T
        """
        e = head.val
        new_head = head.next
        del head.val, head.next
        self.head = new_head
        # pointer adjustments
        if new_head is None:
            self.tail = Node[None]
        else:
            new_head.prev = Node[None]
        self.size -= 1
        return e

    def _unlink_last(self, tail: Node[T]) -> T:
        """
        Unlinks the last Node and returns its data
        :param tail: Node[T]
        :return: element of type T
        """
        e = tail.val
        new_tail = tail.prev
        del tail.val, tail.prev
        self.tail = new_tail
        # pointer adjustments
        if new_tail is None:
            self.head = Node[None]
        else:
            new_tail.next = Node[None]
        self.size -= 1
        return e

    def _unlink(self, n: Node[T]) -> T:
        """
        Unlinks the specified node x and returns its data
        :param n: Node[T]
        :return: element of type T
        """
        assert n is not None
        if n is self.head:
            return self._unlink_first(n)
        if n is self.tail:
            return self._unlink_last(n)
        else:
            for node in self:
                if node.next is n:
                    e = node.next.val
                    next_node = n.next
                    prev_node = node
                    # adjust pointers
                    node.next = next_node
                    next_node.prev = prev_node
                    del n
                    self.size -= 1
                    return e
            else:
                raise LookupError(debug_msg(Debug.Error.LOOKUP, inspect.currentframe()))

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


class HashTable(Generic[T]):
    # Class vars
    keys: int
    size: int
    table: list[LinkedList[T]]

    #
    # Magic Methods
    #
    def __init__(self, size: int = 4):
        self.VALUE_ERR = '\'Key cannot be a negative value\''
        self.keys = 0
        self.size = size
        self.table = [LinkedList[T]() for _ in range(size)]

    def __iter__(self):
        for bucket in self.table:
            yield bucket

    def __next__(self):
        pass

    def __repr__(self):
        return 'n'.join([f'{repr(self.table[i])}' for i in range(self.size)])

    def __str__(self):
        return '\n'.join(str(self.table[i]) for i in range(self.size))

    #
    # Public Methods
    #

    def is_empty(self) -> bool:
        """
        Determines if the table is empty
        :return: bool
        """
        return True if self.keys <= 0 else False

    #
    # Insertions
    def insert(self, k: int, v: T) -> None:
        """
        Inserts a new item into the HashTable
        :param k: key: int
        :param v: value: T
        :return: None
        """
        if k < 0:
            raise ValueError(debug_msg(Debug.Error.KEY_VALUE, inspect.currentframe()))

        # check if resize is required
        if self.keys >= (8 * self.size):
            self._resize(2 * self.size)

        b = self._hash(k)
        self.table[b].prepend(k, v)
        self.keys += 1

    #
    # Lookups
    def search(self, key: int) -> bool:
        """
        Searches the HashTable for an object containing the provided key
        :param key: int
        :return: bool
        """
        # check if valid key
        if key < 0:
            raise ValueError(debug_msg(Debug.Error.VALUE, inspect.currentframe()))
        # find bucket
        b = self._hash(key)
        # perform search
        if self.table[b].node(key, True):
            return True
        # key wasn't found
        return False

    def get(self, key: int) -> T:
        """
        Retrieves an item holding the corresponding key
        :param key: int
        :return: T
        """
        # check if valid key
        if key < 0:
            raise ValueError(debug_msg(Debug.Error.KEY_VALUE, inspect.currentframe()))
        # find bucket
        b = self._hash(key)
        # retrieve data from the LinkedList
        return self.table[b].node(key, True).val

    #
    # Removes
    def remove(self, key: int) -> bool:
        """
        Removes an item holding the given key
        :param key: int
        :return: bool
        """
        # check if valid key
        if key < 0:
            raise ValueError(debug_msg(Debug.Error.KEY_VALUE, inspect.currentframe()))
        # remove the node containing the key
        b = self._hash(key)
        self.table[b].remove(key, True)
        self.keys -= 1

        # check if resize is needed
        if self.size > 4 and self.keys <= (2 * self.size):
            self._resize(int(0.5 * self.size))

        return True

    def clear(self) -> None:
        """
        Clears the HashTable of all data
        :return:
        """
        self.keys = 0
        for bucket in self.table:
            bucket.clear()
        self._resize(4)

    #
    # Statistics
    def stats(self) -> str:
        """
        Generates statistics for the HashTable and returns them in a string
        :return: str
        """
        fill = '\n'
        if self.keys == 0:
            fill += f'\tbucket=1\t{{None}}\n'
            fill += f'\tbucket=2\t{{None}}\n'
            fill += f'\tbucket=3\t{{None}}\n'
            fill += f'\tbucket=4\t{{None}}\n'
        else:
            for i in range(self.size):
                if i == self.size:
                    fill += f'\tbucket={i}\t'
                    fill += '—'.join('[X]' for _ in range(len(self.table[i])))
                    fill += '\n'
                else:
                    fill += f'\tbucket={i}\t'
                    fill += '—'.join('[X]' for _ in range(len(self.table[i])))
                    fill += '\n'
        return (f'[----------\tHashTable Stats\t----------]'
                f'\n\tkeys={repr(self.keys)}'
                f'\n\tsize={repr(self.size)}'
                f'\n\tload={round(self.keys / self.size, 3)}'
                f'\n{fill}')

    #
    # Private Methods
    #

    #
    # Hashing
    def _hash(self, key: int) -> int:
        """
        Returns an integer of the corresponding bucket a key belongs in
        :param key: int
        :return: int
        """
        return key % self.size

    #
    # Resizing
    def _resize(self, new_table_size: int) -> None:
        """
        Performs resizing of the table given a new table size and rehashes in place
        :param new_table_size: int
        :return: None
        """
        old_table_size = len(self.table)
        self.size = new_table_size

        if self.is_empty():
            del self.table[new_table_size:]
            return

        # add new buckets, if table is growing
        if new_table_size > old_table_size:
            self.table.extend([LinkedList[T]() for _ in range(new_table_size - old_table_size)])

        # iterate previous buckets
        for i in range(old_table_size):
            # iterate LinkedList in current bucket
            for node in self.table[i]:
                if node is not Node[None]:
                    kv = (node.key, node.val)
                    b = self._hash(kv[0])
                    self.table[i].remove(node)
                    self.table[b].prepend(kv[0], kv[1])

        # remove empty buckets, if table is shrinking
        if new_table_size < old_table_size:
            del self.table[new_table_size:]
