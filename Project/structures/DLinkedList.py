# class DLinkedList:
#     def __init__(self):
#         self.head = None
#         self.tail = None
#
#     def __repr__(self):
#         nodes = []
#         current_node = self.head
#
#         while current_node is not None:
#             nodes.append(current_node.data)
#             current_node = current_node.next
#
#         nodes.append("None")
#         return " <-> ".join(nodes)
#
#     def append(self, new_item):
#
#     def count(self, item):
#
#     def clear(self):
#
#     def pop(self):
#
#     def popfront(self):
#
#     def prepend(self, new_item):
#
#     def remove(self, item):
#
#     def rotate(self, step):


class DLLNode:
    def __init__(self, data=None):
        self.next = None
        self.prev = None
        self.data = data

    def __repr__(self):
        return self.data

