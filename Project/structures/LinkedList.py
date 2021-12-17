class Node:
    def __init__(self, data: any):
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
        c_node = self.head

        while c_node:
            nodes.append(str(c_node.data))
            c_node = c_node.next

        nodes.append("None")
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

    def append(self, data: any):
        """
        Creates a new Node and appends to the end of this LinkedList\n
        Time Complexity: Worst Case — O(1)\n
        :param data:
        :return: None
        """
        data = Node(data)
        if self.head is None:
            self.head = data
            self.tail = data
        else:
            self.tail.next = data
            self.tail = data

    def clear(self):
        """
        Clears the LinkedList.\n
        Delegates the garbage collector to cleanup unused references\n
        :return: None
        """
        del self.head
        del self.tail

    def pop(self):
        """
        Removes and returns the last node.\n
        Time Complexity: Worst Case — O(n)\n
        :return: Node
        """
        data = self.tail
        c_node = self.head
        while c_node.next is not None:
            c_node = c_node.next
            if c_node.next.next is None:
                c_node.next = None
            self.tail = c_node
        return data

    def pop_front(self):
        """
        Removes and returns the first node\n
        Time Complexity: Worst Case — O(1)\n
        :return: Node
        """
        if self.head is None:
            return self.head
        data = self.head
        self.head = data.next
        return data

    def push(self, data: any):
        """
        Creates a new Node as the head of this LinkedList\n
        Time Complexity: Worst Case — O(1)\n
        :param data: any
        :return: None
        """
        data = Node(data)
        if self.head is None:
            self.head = data
            self.tail = data
        else:
            data.next = self.head
            self.head = data

    def remove(self, data: any):
        """
        Searches the linked list removing the first Node with matching data\n
        Time Complexity: Worst Case — O(n)\n
        :param data: any
        :return: bool
        """
        c_node = self.head
        if c_node is None:
            return False
        while c_node.next is not None:
            if data == c_node.next.data:
                if c_node.next.next is not None:
                    c_node.next = c_node.next.next
                    return True
                else:
                    del c_node.next
                    c_node.next = None
                    self.tail = c_node
                    return True
            c_node = c_node.next
        return False

    def search(self, data: any):
        """
        Searches the LinkedList and returns the Node if found\n
        Time Complexity: Worst Case — O(n)\n
        :param data: any
        :return: Node
        """
        node = self.head
        while node is not None:
            if node.data == data:
                return True
            node = node.next
        return node

    def size(self):
        """
        Iterates the list to find the number of Node(s)\n
        Time Complexity: Worst Case — O(n)\n
        :return: int
        """
        count = 0
        c_node = self.head
        while c_node.next:
            c_node = c_node.next
            count += 1
        return count

    def sort(self):
        """
        Calls a utility to perform merge sort on the LinkedList\n
        Time Complexity: Worst Case - O(n•log(n))\n
        :return: None
        """
        _mergesort(self, self.head)


########################################
#  Utility Functions for Sorting       #
########################################
def _merge(left: Node, right: Node) -> Node:
    """
    Performs a merge of two LinkedLists, inserting Nodes in order and correcting pointers\n
    Time Complexity: Worst Case — O(N+M)\n
    :param left: Node: The head of the left-side LinkedList
    :param right: Node: The head of the right-side LinkedList
    :return: Node: The head of the merged LinkedList
    """
    merged = Node(None)
    temp = merged
    while left is not None and right is not None:
        if left < right:
            temp.next = left
            left = left.next
        else:
            temp.next = right
            right = right.next
        temp = temp.next
    while left is not None:
        temp.next = left
        left = left.next
        temp = temp.next
    while right is not None:
        temp.next = right
        right = right.next
        temp = temp.next
    return merged.next


def _mergesort(linked_list: LinkedList, node: Node) -> Node:
    """
    Merge sort driver code\n
    Time Complexity:    Worst Case — O(N•log(N))\n
    Space Complexity:   Worst Case — O(N)\n
    :param linked_list: LinkedList
    :param node: Node
    :return: Node: The head of the sorted LinkedList
    """
    if node.next is None:
        return node
    mid = _middle(node)
    node2 = mid.next
    mid.next = None
    linked_list.head = _merge(_mergesort(linked_list, node), _mergesort(linked_list, node2))
    return linked_list.head


def _middle(node: Node) -> Node:
    """
    Finds the middle Node in a LinkedList, using a "tortoise and hare" approach\n
    Time Complexity: Worst Case — O(N/2) = O(N)\n
    :param node:
    :return: Node: The middle Node of the LinkedList
    """
    mid_node = node
    end_node = node.next
    while end_node is not None and end_node.next is not None:
        mid_node = mid_node.next
        end_node = end_node.next.next
    return mid_node
