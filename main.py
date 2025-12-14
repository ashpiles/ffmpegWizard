import sys
import json_processor as jp
import event_tree as et
import copy
import flow_layout as fl
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

add_cmd_window = None

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
        side_bar_content.add_child(self.command_pallet)
        side_bar_content.add_child(self.flag_pallet)

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
        self.command_pallet.internal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.command_pallet.internal_layout.setSpacing(2)

        self.update_pallets()


        # Command Zone
        tree.add_child(command_zone_scroll,(0,1))
        current_cmd = make_command("current_command", "", False)
        command_zone_scroll.add_child(current_cmd)
        current_cmd.setStyleSheet("background-color: #262626")


        end_row = QVBoxLayout()
        end_row_spacer = QSpacerItem(0, 40)
        end_row.setAlignment(Qt.AlignmentFlag.AlignBottom)
        run_button = QPushButton()
        add_cmd_button = QPushButton()
        add_cmd_button.setText("Add Command")


        add_cmd_button.clicked.connect(self.add_command_window)
        run_button.setText("Run")
        end_row.addWidget(add_cmd_button)
        end_row.addSpacerItem(end_row_spacer)
        end_row.addWidget(run_button)

        tree.add_child(et.Node("end_row", end_row),(0,2))
        current_cmd.internal_layout.setContentsMargins(20,20,20,20)
        current_cmd.internal_layout.setSpacing(1)

        self.setCentralWidget(tree)
        self.show()

    def add_command_window(self,  name = "Command Name", cmd = "ffmpeg -i in.mkv out.mp4"):
        global add_cmd_window
        add_cmd_window = AddCmdWindow(name, cmd)
        add_cmd_window.command_added.connect(self.update_pallets)


    def update_pallets(self):
        self.flag_pallet.remove_all_children()
        self.command_pallet.remove_all_children()
        self.make_flag_pallet(self.flag_pallet)
        self.make_command_pallet(self.command_pallet)
    

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


    def make_command_pallet(self, node : et.Node):
        commands = jp.processor.get_all_data()["commands"]
        cmd = "ffmpeg"
        for c in commands.items():
            name = c[0]
            for x in c[1]:
                cmd += " " + x["flag"] + " " + x["input"] 
            command_node = make_command(name, cmd)
            node.add_child(command_node)

    
    def make_flag_pallet(self, node : et.Node):
        flags = jp.processor.get_all_data()["flags"]
        for pair in flags.items():
            flag, flag_data = pair
            node.add_child(make_flag(flag, flag_data))


class AddCmdWindow(QWidget):
    command_added = pyqtSignal(str,str)
    def __init__(self, name = "Command Name", cmd = "ffmpeg -i in.mkv out.mp4"):
        super().__init__()
        layout = QVBoxLayout()

        name_box = QTextEdit(name)
        name_box.setMaximumHeight(30)
        name_box.setMaximumWidth(180)
        name_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.name_edit_text = name_box

        edit_box = QTextEdit(cmd)
        edit_box.setMaximumHeight(45)
        edit_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.cmd_edit_text = edit_box

        push_button = QPushButton()
        push_button.setText("Add Command")
        push_button.setMaximumHeight(50)
        push_button.setMaximumWidth(100)
        push_button.clicked.connect(self.on_click)

        layout.addWidget(name_box)
        layout.addWidget(edit_box)
        layout.addWidget(push_button)

        self.setLayout(layout)
        self.show()
     
    def on_click(self):
        name = self.name_edit_text.toPlainText()
        cmd = self.cmd_edit_text.toPlainText()
        flags = jp.CmdParser(cmd).flags
        jp.processor.add_command(name, cmd)
        for f in flags:
            jp.processor.add_flag(f["flag"])
        self.command_added.emit(name,cmd)


def make_command(name, cmd, front = True):
    node = CommandNode(name, cmd)
    label = QLabel("")

    if not front:
        label.setText("ffmpeg")
        label.setFixedHeight(30)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        node.internal_layout.addWidget(label)
        node.internal_layout.setSpacing(3)
        return node 

    label.setText(name)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    label.setContentsMargins(5,0,5,0)
    label_font = QFont()
    label_font.setBold(True)
    label.setFont(label_font)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    node.internal_layout.addWidget(label)
    node.setStyleSheet("background-color: #2f2f30")
    node.setAcceptDrops(False)
    return node 


def make_flag(flag, value, front = True):
    if flag == "":
        flag = "out"
    flag_layout = QVBoxLayout()
    node = FlagNode(flag, value, flag_layout)

    label = QLabel(flag)
    label_font = QFont()
    label_font.setBold(True)
    label.setFont(label_font)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    input_box = QTextEdit()

    if type(value) is str:
        input_box.setText(value)
    input_box.setFixedSize(80,30)
    def updateEditText():
        width = input_box.width()
        height = input_box.height()
        str_len = len(input_box.toPlainText())
        len_cap = 4

        width = 80 if str_len <= len_cap*4 else 160
        height = 30 if str_len <= len_cap*2 else 60
        input_box.setFixedWidth(width)
        input_box.setFixedHeight(height)
        node.input_value = input_box.toPlainText()

    updateEditText()
    input_box.textChanged.connect(updateEditText)

    if front:
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label.setContentsMargins(5,0,5,0)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        flag_layout.addWidget(label)
        flag_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    else:
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedHeight(30)
        label.setMinimumWidth(80)
        flag_layout.addWidget(label)
        flag_layout.addWidget(input_box)

    if front:
        node.setStyleSheet("background-color: #2f2f30")
        node.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    else:
        node.doubleClicked.connect(lambda : input_box.setHidden(not input_box.isHidden()))
        node.setBaseSize(40,50)
        node.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        node.setContentsMargins(10, 0, 10, 30)

    return node


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
        elif not self.has_child(widget) and type(widget) is CommandNode:
            widget.update_flags()
            window.add_command_window(widget.name, jp.toCommand(widget.flags))
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
    doubleClicked = pyqtSignal()
    def __init__(self, name, input_value, layout):
        self.flag = name
        self.input_value = input_value
        super().__init__(name, layout)
    

    def mouseDoubleClickEvent(self, e):
        if e.button() == e.buttons().LeftButton:
            self.doubleClicked.emit()
        return super().mouseDoubleClickEvent(e)


class CommandNode(DraggableNode):
    def __init__(self, name : str, cmd : str):
        super().__init__(name, fl.FlowLayout())
        self.setAcceptDrops(True)
        parser = jp.CmdParser(cmd)
        self.flags = parser.flags
        self.cmd = cmd

    def update_flags(self):
        self.flags = []
        for n in range(self.internal_layout.count()):
            w = self.internal_layout.itemAt(n)
            if w is None:
                return
            widget = w.widget()
            if type(widget) is FlagNode:
                self.flags.append({"flag":widget.flag, "input":widget.input_value})

    def replace_command(self, cmd_node):
        if self.name == "current_command.0":
            self.flags = []
            self.remove_all_children(True)

            for x in cmd_node.flags:
                self.add_child(make_flag(x["flag"],x["input"], False))
                self.flags.append({x["flag"],x["input"]})
        else:
            global add_cmd_window
            add_cmd_window = AddCmdWindow("New Command",cmd_node.cmd)

    
    def add_child(self, node, at=-1):
        if type(node) is FlagNode:
            return super().add_child(node, at)
        elif type(node) is DraggableNode:
                return
        return 
    
    def dragEnterEvent(self, e):
        e.accept()
    
    def dropEvent(self, e):
        pos = e.position().toPoint()
        widget = e.source()
        on_self = self.has_child(widget)

        self.remove_child(widget)
        layout = self.internal_layout

        if isinstance(widget, CommandNode):
            self.replace_command(widget)

        insert_index = layout.count()  # default = append

        for i in range(1, layout.count()):
            item = layout.itemAt(i)
            w = item.widget()
            if w is None:
                continue

            rect = w.geometry()
            if rect.contains(pos):
                insert_index = i
                break

        if on_self:
            self.add_child(widget, insert_index)
        elif isinstance(widget, FlagNode):
            self.add_child(make_flag(widget.flag, widget.input_value, False), insert_index)

        e.accept()


app = QApplication(sys.argv)

window = MainWindow()

app.exec()