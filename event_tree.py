import sys
import wizard_util as util
import re
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *



#======================================================================================
# Allows for non-permanent widgets to communicate to one another with events
# a Node is given a signal, this signal is the function called on the event trigger
# When a node triggers an event it is given to the tree
# which then finds the correct node and launches that nodes stored func
#======================================================================================

EventTreeNodeEventType = QEvent.registerEventType()
EventTreeNodeHandShakeType = QEvent.registerEventType()

# Nodes send's an event to the tree
# the tree finds the target node and delivers data
class EventTreeNodeEvent(QEvent):
    def __init__(self, package : tuple):
        super().__init__(EventTreeNodeEventType)
        self.sender_id, self.target_path, self.node_data = package
   
class Node(QWidget):
    on_node_move = pyqtSignal(str, str)
    on_node_event = pyqtSignal(int, str, list)

    def __init__(self, name : str, widget : QWidget):
        super().__init__()
        # the 'file path' to this node
        self.tree_path : str = ""
        # the name of this node
        self.NAME = name
        # the embeded widget
        self.widget_socket : QWidget = widget
        # the children of nodes by the node's name
        self._children = []
        self._tree_ref = None
    
    def send_event(self, target_path : str, data : list):
        QApplication.postEvent(self._tree_ref, EventTreeNodeEvent((id(self), target_path, data)))

    # We accept a function as the move request
        # if things get advanced move request funcs can be put on a queue and use cmd pattern
    def accept_move_request(self, move_request):
        from_path, to_path = move_request()
        self.on_node_move.emit(from_path, to_path)
    
    def remove_child(self, child_name : str):
        child = self.get_child(child_name)
        child._children = []
        child.destroy(True, True)
        self._children.remove(child)
        return
    
    # it would be better to implement the vistor pattern here
    # however we cannot ensure types so its not worth it until i figure that out
    def _add_child(self, node, tree):
        node._tree_ref = tree
        node.tree_path = self.tree_path + "/" + node.NAME
        self._children.append(node)
    
    def get_children(self) -> list:
        return self._children
    
    def get_child(self, child_name: str):
        for child in self._children:
            if child.NAME == child_name:
                return child
        return None


    def _receive_event_data(self, node_id, target_path, data):
        self.on_node_event.emit(node_id, target_path, data)
    


class EventTree(QWidget):
    def __init__(self, root_widget : QWidget):
        super().__init__()
        self.ROOT : Node = Node("root", root_widget) 
        self.ROOT.tree_path = "root"
        self.ROOT._tree_ref = self

    def add_node_to(self, node : Node, node_path : str):
        parent = self.get_node(node_path)
        if parent:
            parent._add_child(node, self)
            return node
    
    def remove_node(self, node_path : str):
        parent_match, child_match = re.findall(r"((?:/|^)[\w/]+/)([\w/]+$)", node_path)[0]
        parent = self.get_node(parent_match) # why are we not getting the node?
        child = parent.get_child(child_match)
        child.remove_from_tree()

    def get_node(self, node_path : str) -> Node:
        return self._get_node(self.ROOT, node_path)

    def _get_node(self, current_node: Node, destination_path: str) -> Node:
        # If we found the exact node
        if current_node.tree_path == destination_path:
            return current_node

        # Search children
        for child in current_node.get_children():
            result = self._get_node(child, destination_path)
            if result is not None:
                return result

        return None

     
    def _get_sub_path(self, sub_path : str, main_path : str) -> str:
        if (sub_path is not None) & (main_path is not None):
            sub_path = re.match(r"(?:/|^)" + sub_path + r"(?=/|$)", main_path)
            if sub_path:
                return sub_path[0]
        return ""

        
    def get_children_of(self, node_path : str):
        return self.get_node(node_path).get_children()

    def move_node_to(self, from_path : str, to_path : str):
        node = self.get_node(from_path)
        to_node = self.get_node(to_path) # i should have a function that checks if a path is real
        if node is not None and to_node is not None:
            self.remove_node(from_path)
            self.add_node_to(node, to_path)
        return
    
    # Event override
    def event(self, e):
        if e.type() == EventTreeNodeEventType:
            target = self.get_node(e.target_path)
            if target:
                target._receive_event_data(e.sender_id, e.target_path, e.node_data)
            return True
        return super().event(e)


    

app = QApplication(sys.argv)

tree = EventTree(QWidget())

for i in range(0,10):
    node1 = tree.add_node_to(Node("A"+str(i),QWidget()),"root")
    for j in range(0,4):
        node2 = tree.add_node_to(Node("B"+str(j),QWidget()), node1.tree_path)
        for y in range(0,2):
            node3 = tree.add_node_to(Node("C"+str(y),QWidget()), node2.tree_path)
            if node3.tree_path == "root/A5/B3/C0":
                sender = node3

print(tree.ROOT)

node3.on_node_event.connect(lambda x,y,z: print(x,y,z[0]))
sender.send_event(node3.tree_path, ["hello world"])

app.exec()