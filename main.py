
import sys
import wizard_util as util
import re
import event_tree
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

processor = util.processor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFMPEG Wizard")
        cmd_list = InteractableListWidget()
        for i in range(0,10):
            label = QLabel("Test"+str(i))
            node = event_tree.Node(label.text(), label)
            node.socket_events.hovered.connect(lambda w: print("hover on" + w.text()))
            node.socket_events.unhovered.connect(lambda w: print("hover off" + w.text()))
            cmd_list.add_to_path(node, "root")
        self.setCentralWidget(cmd_list)
        self.show()


class InteractableListWidget(QWidget):
    def __init__(self):
        super().__init__()

        # container inside scroll area
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)

        # scroll setup
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)

        # main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.scroll)
        self.setLayout(self.main_layout)

        # tree, but DON'T give it control of container layout!
        self._tree = event_tree.EventTree(self.container, self.container_layout)

        self.show()

    # All i need to do is set the children as part of the layout

    def get_root(self):
        return self._tree.ROOT
    
    def add_to(self, node : event_tree.Node, parent : event_tree.Node):
        parent.add_child(node, self._tree)

    def add_to_path(self, node : event_tree.Node, path : str):
        parent = self._tree.get_node(path)
        if parent:
            parent.add_child(node,self._tree)
    
    # i have to create a hover & click on event
    # also i need to see if the add works

app = QApplication(sys.argv)

window = MainWindow()

app.exec()