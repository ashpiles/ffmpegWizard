import sys
import re
import copy
import json_processor as jp
import event_tree as et
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFMPEG Wizard")
        main_layout = QGridLayout()
        side_bar_layout = QVBoxLayout()
        tree = et.EventTree(main_layout)
        side_bar = et.Node("left_side_bar", side_bar_layout)
        side_bar_toolbar = et.Node("toolbar", QHBoxLayout())
        flag_palet_con = ScrollNode("scroll", QVBoxLayout())
        flag_palet = DragBoxNode("box", QVBoxLayout())

        tree.add_child(side_bar,(0,0))

        # Side Bar
        #----------------------------------
        side_bar.add_child(side_bar_toolbar)
        side_bar.add_child(flag_palet_con)
        side_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        side_bar_toolbar.internal_layout.addWidget(QPushButton("Flags"))
        side_bar_toolbar.internal_layout.addWidget(QPushButton("Commands"))
        flag_palet_con.add_child(flag_palet)
        self.make_flag_pallet(flag_palet)

        # Command Zone
        command_zone = DragBoxNode("command_zone", QVBoxLayout())
        command_zone.setStyleSheet("background-color: #262626")
        tree.add_child(command_zone,(0,1))
        command_layout = QHBoxLayout()
        current_cmd = CommandNode("current_command", command_layout)
        command_zone.add_child(current_cmd)
        command_layout.setContentsMargins(20,20,20,20)
        command_layout.setSpacing(2)

        self.setCentralWidget(tree)
        self.show()
    
    def make_flag_pallet(self, node : et.Node):
        flags = jp.processor.get_all_data()["flags"]
        for pair in flags.items():
            flag, flag_data = pair 
            node.add_child(make_flag(flag, flag_data))

def make_flag(flag, value):
    if flag is "":
        flag = "out"
    label = QLabel(flag)
    flag_layout = QVBoxLayout()
    flag_layout.addWidget(label)
    node = FlagNode(flag, flag_layout)
    return node


# now we need to detect when are moving to a different part of the tree
# when a node is empty it is removed
# if i drag out all the draggable nodes make sure the drag box still lives

#[X] keep drag box alive when empty
#[X] have nodes move in the tree when dragged
#[X] implement JSON parsing
#[ ] command zone
# - can re arrange / edit flags
# -   
#[ ] flag palet
    #[ ] creating a flagnode
# - flag is a stacklayer
# - switch to input on db click
# - the move function should handle this completely
#[ ] command palet
# - vbox with a hbox for buttons that switch the stacked widget
# - the cmd palet is a dragbox made of cmd draggables & flag draggables
#[ ] highlight on hover



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

class FlagNode(DraggableNode):
    def __init__(self, name, layout):
        self.flag = name
        self.value = []
        super().__init__(name, layout)
    
class CommandNode(DraggableNode):
    def __init__(self, name, layout ):
        super().__init__(name, layout)
        self.setAcceptDrops(True)

    
    def dragEnterEvent(self, e):
        e.accept()
    
    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()
        on_self = self.has_child(widget)
        if on_self:
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
        if on_self:
            self.add_child(widget, n)
        elif type(widget) == FlagNode:
            self.add_child(make_flag(widget.flag, widget.value))
            # make a flag factory
            # get the current info and send over a new node with relevant info

        print(type(widget))
        e.accept()



app = QApplication(sys.argv)

window = MainWindow()

app.exec()