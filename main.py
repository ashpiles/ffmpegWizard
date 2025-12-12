import sys
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
        self.toggle_layout = QStackedLayout()
        tree = et.EventTree(main_layout)
        side_bar = et.Node("left_side_bar", side_bar_layout)
        side_bar_toolbar = et.Node("toolbar", QHBoxLayout())
        side_bar_scroll = ScrollNode("scroll", QVBoxLayout())
        side_bar_content = et.Node("left_side_bar_content", self.toggle_layout)
        command_zone_scroll = ScrollNode("scroll", QVBoxLayout())
        self.flag_pallet = DragBoxNode("flag_pallet", QVBoxLayout())

        self.command_pallet = DragBoxNode("command_pallet", QVBoxLayout())

        self.flag_button = QPushButton("Flags")
        self.command_button = QPushButton("Commands")
        self.current_button = "Commands"


        # Side Bar
        #----------------------------------
        tree.add_child(side_bar,(0,0))
        tree.internal_layout.setColumnStretch(0, 10)
        side_bar.add_child(side_bar_toolbar)
        side_bar.add_child(side_bar_scroll)
        side_bar_scroll.add_child(side_bar_content)
        side_bar_content.add_child(self.flag_pallet)
        side_bar_content.add_child(self.command_pallet)

        self.flag_button.setCheckable(True)
        self.command_button.setCheckable(True)
        self.command_button.setChecked(True)
        self.flag_button.clicked.connect(self.switch_side_bar)
        self.command_button.clicked.connect(self.switch_side_bar)
        side_bar_toolbar.internal_layout.addWidget(self.flag_button)
        side_bar_toolbar.internal_layout.addWidget(self.command_button)
        side_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)


        self.flag_pallet.internal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.flag_pallet.internal_layout.setSpacing(2)
        self.make_flag_pallet(self.flag_pallet)



        # Command Zone
        command_zone = DragBoxNode("command_zone", QVBoxLayout())
        command_zone_scroll.add_child(command_zone)
        command_zone.setStyleSheet("background-color: #262626")
        tree.add_child(command_zone_scroll,(0,1))
        end_row = QVBoxLayout()
        end_row_spacer = QSpacerItem(0, 40)
        end_row.setAlignment(Qt.AlignmentFlag.AlignBottom)
        run_button = QPushButton()
        run_button.setText("Run")
        end_row.addWidget(run_button)
        end_row.addSpacerItem(end_row_spacer)

        tree.add_child(et.Node("end_row", end_row),(0,2))
        current_cmd = make_command("current_command", r"ffmpeg -i in.mp4 -itsoffset 3.84 -i in.mp4 -map 0:v -map 1:a -vcodec copy -acodec copy out.mp4", False)
        command_zone.add_child(current_cmd)
        current_cmd.internal_layout.setContentsMargins(20,20,20,20)
        current_cmd.internal_layout.setSpacing(1)
        current_cmd.internal_layout.setAlignment

        self.setCentralWidget(tree)
        self.show()
    
    def switch_side_bar(self, button):
        match self.current_button:
            case "Commands":
                self.current_button = "Flags"
                self.command_button.setChecked(False)
                self.flag_button.setChecked(True)
                self.toggle_layout.setCurrentWidget(self.flag_pallet)
            case "Flags":
                self.current_button = "Commands"
                self.command_button.setChecked(True)
                self.flag_button.setChecked(False)
                self.toggle_layout.setCurrentWidget(self.command_pallet)
            case default:
                pass




    
    def make_flag_pallet(self, node : et.Node):
        flags = jp.processor.get_all_data()["flags"]
        for pair in flags.items():
            flag, flag_data = pair
            node.add_child(make_flag(flag, flag_data))

def make_command(name, cmd, front = True):
    node = CommandNode(name, cmd)
    container = et.Node("command_container", QHBoxLayout())
    ffmpeg_label = QLabel("ffmpeg")
    ffmpeg_label.setFixedSize(60,30)
    ffmpeg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ffmpeg_label.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
    container.internal_layout.addWidget(ffmpeg_label)
    container.add_child(node)
    node.add_child(make_flag("-i", "", front))
    return container

def make_flag(flag, value, front = True):
    if flag == "":
        flag = "out"
    flag_layout = QHBoxLayout()

    label = QLabel(flag)
    input_box = QTextEdit()
    input_box.setFixedSize(40,30)
    def autoResize():
        width = input_box.width()
        height = input_box.height()
        str_len = len(input_box.toPlainText())
        len_cap = 4

        width = 40 if str_len <= len_cap else 80
        height = 30 if str_len <= len_cap*2 else 60

        input_box.setFixedWidth(width)
        input_box.setFixedHeight(height)
    input_box.textChanged.connect(autoResize)

    if front:
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label.setContentsMargins(5,0,5,0)
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        flag_layout.addWidget(label)
        flag_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    else:
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flag_layout.addWidget(label)
        flag_layout.addWidget(input_box)


    node = FlagNode(flag, flag_layout)
    if front:
        node.setStyleSheet("background-color: #2f2f30")
        node.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    else:
        node.setBaseSize(40,50)
        node.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    return node

#[X] Command Tab
#[ ] Command pallet
#[ ] Drag and drop commands
# - dragging a cmd into pallet adds
# - draggin a cmd into zone adds all flags
#[ ] Command Zone dbl click on flag to switch to input
#[ ] Add command window
#[ ] clear command zone
#[ ] Command Zone scroll area
# - turn it into a grid box
#[ ] formatting command zone
#[ ] Run Button
#[ ] in & out buttons

# Source - https://stackoverflow.com/a
# Posted by musicamante, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-11, License - CC BY-SA 4.0




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
        if not self.has_child(widget) and type(widget) is FlagNode:
            widget.deleteLater()
            widget.remove_self()
            e.accept()
            return
        elif type(widget) is CommandNode:
            e.accept()
            return
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
        self.command_pos = (0,0)
        self.value = []
        super().__init__(name, layout)
    
class CommandNode(DraggableNode):
    def __init__(self, name : str, cmd : str):
        super().__init__(name, QHBoxLayout())
        self.setAcceptDrops(True)
        parser = jp.CmdParser(cmd)
        self.flags = parser.flags

    def add_child(self, node, at=-1):
        if type(node) is FlagNode:
            return super().add_child(node, at)
        elif type(node) is DraggableNode:
                return
        return 
    
    def dragEnterEvent(self, e):
        e.accept()
    
    # when a flag is being moved into a command
    def dropEvent(self, e):
        pos = e.position()
        widget = e.source()
        on_self = self.has_child(widget)
        self.remove_child(widget)
        layout = self.internal_layout

        n = 0
        for n in range(layout.count()):
            w = layout.itemAt(n).widget()
    
            if pos.y() > w.y() + w.size().height() // 2:
                n = len(layout.children())
                break
            elif pos.x() < w.x() + w.size().width() // 2:
                break
        else:
            n +=1
    
        
        if on_self:
            self.add_child(widget, n)
        elif type(widget) == FlagNode:
            self.add_child(make_flag(widget.flag, widget.value, False), n)

        e.accept()



app = QApplication(sys.argv)

window = MainWindow()

app.exec()