class Node:
    def __init__(self, key: int, data: any):
        self.id = key
        self.val = data
        self.pointer = None

    def __str__(self):
        return str(self.val)

    def __eq__(self, other):
        if type(self.data) is not type(other.data):
            raise Exception("Package=structures, Module=LinkedList.Node -> Equality operator called on varying data "
                            "types")
        return self.data == other.data

    def __ne__(self, other):
        if type(self.data) is not type(other.data):
            raise Exception("Package=structures, Module=LinkedList.Node -> Equality operator called on varying data "
                            "types")
        return self.data != other.data

    def __lt__(self, other):
        if type(self.data) is not type(other.data):
            raise Exception("Package=structures, Module=LinkedList.Node -> Equality operator called on varying data "
                            "types")
        return self.data < other.data

    def __gt__(self, other):
        if type(self.data) is not type(other.data):
            raise Exception("Package=structures, Module=LinkedList.Node -> Equality operator called on varying data "
                            "types")
        return self.data > other.data

    def __le__(self, other):
        if type(self.data) is not type(other.data):
            raise Exception("Package=structures, Module=LinkedList.Node -> Equality operator called on varying data "
                            "types")
        return (self.data < other.data) or (self.data == other.data)

    def __ge__(self, other):
        if type(self.data) is not type(other.data):
            raise Exception("Package=structures, Module=LinkedList.Node -> Equality operator called on varying data "
                            "types")
        return (self.data > other.data) or (self.data == other.data)

    def __contains__(self, other):
        if type(self.data) is not type(other.data):
            raise Exception("Package=structures, Module=LinkedList.Node -> Equality operator called on varying data "
                            "types")
        return self.data == other

    @property
    def key(self):
        return self.id

    @key.setter
    def key(self, k):
        self.id = k

    @key.deleter
    def key(self):
        self.id = None

    @property
    def data(self):
        return self.val

    @data.setter
    def data(self, val):
        self.val = val

    @data.deleter
    def data(self):
        self.val = None

    @property
    def next(self):
        return self.pointer

    @next.setter
    def next(self, node):
        self.pointer = node

    @next.deleter
    def next(self):
        self.pointer = None


class LinkedList:
    start: Node
    end: Node

    def __init__(self, head=None, tail=None):
        self.start = head
        self.end = tail

    def __str__(self):
        nodes = []
        node = self.head

        while node:
            nodes.append(str(node.data))
            node = node.next

        nodes.append("None\n")
        return " -> ".join(nodes)

    @property
    def head(self):
        return self.start

    @head.setter
    def head(self, node: Node):
        self.start = node

    @head.deleter
    def head(self):
        self.start = None

    @property
    def tail(self):
        return self.end

    @tail.setter
    def tail(self, node: Node):
        self.end = node

    @tail.deleter
    def tail(self):
        self.end = None

    def push(self, key: int, data: any):
        """
        Creates a new Node as the head of this LinkedList\n
        Time Complexity: Worst Case — O(1)\n
        :param key: int
        :param data: any
        :return: None
        """
        data = Node(key, data)
        if self.head is None:
            self.head = data
            self.tail = data
        else:
            data.next = self.head
            self.head = data

    def remove(self, key: int):
        """
        Searches the linked list removing the first Node with matching key\n
        Time Complexity: Worst Case — O(n)\n
        :param key: int
        :return: bool
        """
        node = self.head
        if node is None:
            self.tail = None
            return False
        if node.key == key:
            self.head = node.next
            node = None
            return True
        while node.next is not None:
            if node.next.key == key:
                if node.next.next is not None:
                    node.next = node.next.next
                    return True
                else:
                    node.next = None
                    self.tail = node
                    return True
            node = node.next
        return False

    def search(self, key: int = None):
        """
        Searches the LinkedList and returns the Node if found\n
        Can be searched by key or data
        Time Complexity: Worst Case — O(n)\n
        :param: key int
        :param: data any
        :return: Node
        """
        node = self.head
        while node is not None:
            if node.key == key:
                return node.data
            node = node.next
        return None

    def size(self):
        """
        Iterates the list to find the number of Node(s)\n
        Time Complexity: Worst Case — O(n)\n
        :return: int
        """
        if self.head is not None and self.head.next is None:
            return 1

        count = 0
        c_node = self.head
        while c_node:
            count += 1
            c_node = c_node.next
        return count
