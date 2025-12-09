
import sys
import wizard_util as util
import re
import event_tree as et
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

processor = util.processor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFMPEG Wizard")
        tree = et.EventTree(QVBoxLayout())

        # the weakeness is that we only go exactly one deep
        # what if we simply add child node layouts to our own

        # a node must display its widget
        for i in range(0,10):
            label = QLabel("Test"+str(i))
            label_layout = QHBoxLayout()
            label_layout.addWidget(label)
            node = et.Node(label.text(), label_layout)
            node.socket_events.hovered.connect(lambda w: print("hover on" + w.NAME))
            node.socket_events.unhovered.connect(lambda w: print("hover off" + w.NAME))
            tree.add_child(node)
            for x in range(0,3):
                label2 = QLabel("test"+str(x))
                label2_layout = QVBoxLayout()
                label2_layout.addWidget(label2)
                node2 = et.Node(label2.text(), label2_layout)
                node.add_child(node2)
                for y in range(0,2):
                    label3 = QLabel("t"+str(y))
                    label3_layout = QGridLayout()
                    label3_layout.addWidget(label3)
                    node3 = et.Node(label3.text(), label3_layout)
                    node2.add_child(node3)
 

        self.setCentralWidget(tree)
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
        self._tree = et.EventTree(self.container, self.container_layout)

        self.show()

    # All i need to do is set the children as part of the layout

    def get_root(self):
        return self._tree.ROOT
    
    def add_to(self, node : et.Node, parent : et.Node):
        parent.add_child(node, self._tree)

    def add_to_path(self, node : et.Node, path : str):
        parent = self._tree.get_node(path)
        if parent:
            parent.add_child(node,self._tree)
    
    # i have to create a hover & click on event
    # also i need to see if the add works

app = QApplication(sys.argv)

window = MainWindow()

app.exec()