import sys
import wizard_util
from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import *
from PyQt6.QtCore import *


processor = wizard_util.JsonProcessor()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFMPEG Wizard")

        main_layout = QHBoxLayout()
        cmd_list_layout = QVBoxLayout()
        user_input_layout = QVBoxLayout()
        user_input_upper_layout = QGridLayout()
        user_input_lower_layout = QGridLayout()


        cmd_list = CmdListWidget()
        cmd_list_layout.addWidget(cmd_list)

        text_box = QTextEdit()
        text_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        text_box.setFixedHeight(30)

        add_cmd = AddCmdButton()

        self.input_list = CmdInputListWidget()

        output_button = QPushButton()
        output_button.setText("Output")
        output_button.setFixedSize(100, 40)

        run_button = QPushButton()
        run_button.setText("Run")
        run_button.setFixedSize(100, 40)


        user_input_upper_layout.addWidget(text_box,1,0)
        user_input_upper_layout.addWidget(add_cmd,0,1)

        user_input_lower_layout.addWidget(self.input_list,0,0)
        user_input_lower_layout.addWidget(output_button,0,1)
        user_input_lower_layout.addWidget(run_button,2,0)

        cmd_list_layout.setStretch(0, 1)
        user_input_layout.addLayout(user_input_upper_layout)
        user_input_layout.addLayout(user_input_lower_layout)
        main_layout.addLayout(cmd_list_layout)
        main_layout.addLayout(user_input_layout)
        main_layout.setStretch(0,1)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.show()

    def event(self, e):
        if e.type() == wizard_util.CmdChangedEventType:
            self.input_list.update_list(e.cmd_input)
            return True
        return super().event(e)


#                         Widgets
# ============================================================ #


class CmdInputListWidget(QWidget):
    def __init__(self):
        super().__init__()
        global processor
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.list_layout = QVBoxLayout()

        self.setLayout(self.list_layout)
    
    def update_list(self, input_list : dict):
        for (flag, value) in input_list.items():
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(flag))
            row_layout.addWidget(QTextEdit())
            self.list_layout.addLayout(row_layout)

    

class CmdListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        global processor
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # i need a way to convert cmds to json and json to cmds
        for command in processor.get_all_commands():
            item = QListWidgetItem(command)
            self.addItem(item)

        scroll_bar = QScrollBar(self)
        scroll_bar.setStyleSheet("background : gray;")
        self.setVerticalScrollBar(scroll_bar)

        self.itemClicked.connect(self.cmd_clicked)
    
    def cmd_clicked(self, item : QListWidgetItem):
        global processor
        current_cmd = {item.text() : processor.get_command(item.text())}
        QApplication.postEvent(window, wizard_util.CmdChangedEvent(current_cmd))

class AddCmdButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.geometry = QRect(20,20,10,10)
    
 


app = QApplication(sys.argv)

window = MainWindow()

app.exec()