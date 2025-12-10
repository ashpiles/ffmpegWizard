
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
        tree = et.EventTree(QHBoxLayout())
        box = DragBoxNode("box", QVBoxLayout())
        box1 = DragBoxNode("box1", QVBoxLayout())

        scroll = ScrollNode("scroll", QVBoxLayout())
        scroll1 = ScrollNode("scroll1", QVBoxLayout())
        tree.add_child(scroll)
        tree.add_child(scroll1)
        scroll.add_child(box)
        scroll1.add_child(box1)

        self.make_box(box)
        self.make_box(box1)

        self.setCentralWidget(tree)
        self.show()

    def make_box(self, box):
        for i in range(0,1):
            label = QLabel("Test"+str(i))
            label_layout = QHBoxLayout()
            label_layout.addWidget(label)
            node = DraggableNode(label.text(), label_layout)
            node.socket_events.hovered.connect(lambda w: print("hover on" + w.NAME))
            node.socket_events.unhovered.connect(lambda w: print("hover off" + w.NAME))
            box.add_child(node)
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


# now we need to detect when are moving to a different part of the tree
# when a node is empty it is removed
# if i drag out all the draggable nodes make sure the drag box still lives

#[X] keep drag box alive when empty
#[X] have nodes move in the tree when dragged
#[ ] implement JSON parsing
#[ ] make a flag node button
#[ ] flag palet
# - creating a flagnode
# - flag is a stacklayer
# - switch to input on db click
# - the move function should handle this completely
#[ ] command palet
# - vbox with a hbox for buttons that switch the stacked widget
# - the cmd palet is a dragbox made of cmd draggables & flag draggables
#[ ] highlight on hover
#[ ] command zone
# - a box that scales with the window !last!
# - orders commands to wrap around the box
# - can re arrange / edit flags


class DraggableNode(et.Node):
    def __init__(self, name : str, layout : QLayout):
        super().__init__(name, layout)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.exec(Qt.DropAction.MoveAction)

class DragBoxNode(et.Node):
    def __init__(self, name : str, layout : QLayout):
        super().__init__(name, layout)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.accept()
    
    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()
        self.remove_child(widget)
        

        n = 0
        for n in range(self.internal_layout.count()):
            w = self.internal_layout.itemAt(n).widget()
            if pos.y() < w.y() + w.size().height() // 2:
                break
            elif pos.x() < w.x() + w.size().width() // 2:
                break
        else:
            n +=1
        self.add_child(widget, n)
        e.accept()


class ScrollNode(et.Node):
    def __init__(self, name: str, layout: QLayout):
        super().__init__(name, layout)

        self.container = QWidget()
        self.container.setLayout(self.internal_layout)

        # scroll setup
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.scroll)
        self.setLayout(self.main_layout)


class InteractableListWidget(QWidget):
    def __init__(self):
        super().__init__()



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