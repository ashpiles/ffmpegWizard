import sys
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

class NodeItemEventFilter(QObject):
    hovered = pyqtSignal(QWidget)
    unhovered = pyqtSignal(QWidget)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            self.hovered.emit(obj)
        if event.type() == QEvent.Type.Leave:
            self.unhovered.emit(obj)
        return super().eventFilter(obj, event)

# Nodes send's an event to the tree
# the tree finds the target node and delivers data
class EventTreeNodeEvent(QEvent):
    def __init__(self, package : tuple):
        super().__init__(EventTreeNodeEventType)
        self.sender_id, self.target_path, self.node_data = package
   

class Node(QWidget):
    on_node_move = pyqtSignal(QWidget, QWidget)
    on_node_event = pyqtSignal(int, str, list)

    def __init__(self, name : str, layout : QLayout):
        super().__init__()

        if layout is None:
            layout = QVBoxLayout()

        self.name = name
        self.tree_path = ""
        self._children : QWidget = []
        self._tree_ref = None
        self.socket_events = NodeItemEventFilter()
        self.installEventFilter(self.socket_events)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.internal_layout = layout
        self.setLayout(self.internal_layout)

    def __getitem__(self, key : int):
        return self._children[key]

    def get_tree(self):
        return self._tree_ref
    
    def send_event(self, target_path : str, data : list):
        QApplication.postEvent(self._tree_ref, EventTreeNodeEvent((id(self), target_path, data)))

    # We accept a function as the move request
        # if things get advanced move request funcs can be put on a queue and use cmd pattern
    def accept_move_request(self, move_request):
        from_path, to_path = move_request()
        self.on_node_move.emit(from_path, to_path)
    
    def has_child(self, child):
        for x in self._children:
            if x.name == child.name:
                if x is child:
                    return True 
        return False
    
    def remove_self(self):
        parent_path = self.tree_path.removesuffix("/"+self.name)
        parent = self._tree_ref.get_node(parent_path)
        for child in self._children:
            self.remove_child(child)
        parent.remove_child(self)

    def remove_child(self, child):
        if self.has_child(child):
            self.internal_layout.removeWidget(child)
            self._children.remove(child)
        return child
    
    def remove_all_children(self, delete_flag = False):
        for i in range(len(self._children)):
            child = self._children.pop(0)
            self.internal_layout.removeWidget(child)
            if delete_flag:
                child.deleteLater()
    
    def add_child(self, node : QWidget, at = -1):
        # Ensure every path is unique
        digit_match = re.findall(r"(?<=\.)(\d*)$", node.name)
        num = 0 
        if digit_match:
            num = digit_match[0]
            num = int(num)+1
        node.name = node.name+"."+str(num)

        node._tree_ref = self._tree_ref
        node.tree_path = self.tree_path + "/" + node.name

        if type(self.internal_layout) is type(QGridLayout()):
            x,y = at
            self.internal_layout.addWidget(node,x,y)
        elif type(at) is int and at >= 0:
            self.internal_layout.insertWidget(at, node)
        else:
            self.internal_layout.addWidget(node)

        self._children.append(node)
    
    def get_children(self) -> list:
        return self._children
    
    def get_child(self, child_name: str):
        for child in self._children:
            if child.name == child_name:
                return child
        return None
    
    def _receive_event_data(self, node_id, target_path, data):
        self.on_node_event.emit(node_id, target_path, data)
    


class EventTree(Node):
    def __init__(self, root_layout : QLayout):
        super().__init__("root", root_layout)
        self.tree_path = "root"
        self._tree_ref = self
    
    def add_node_to(self, node : Node, node_path : str):
        parent = self.get_node(node_path)
        if parent:
            parent.add_child(node, self)
            return node
    
    def remove_node(self, node_path : str):
        parent_match, child_match = re.findall(r"((?:/|^)[\w/]+/)([\w/]+$)", node_path)[0]
        parent = self.get_node(parent_match) # why are we not getting the node?
        child = parent.get_child(child_match)
        child.remove_from_tree()

    def get_node(self, node_path : str) -> Node:
        return self._get_node(self, node_path)

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

     
    def get_sub_path(self, sub_path : str, main_path : str) -> str:
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
