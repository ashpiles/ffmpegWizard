import sys
import wizard_util as util
import re
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

processor = util.processor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFMPEG Wizard")

        main_layout = QHBoxLayout()
        cmd_list_layout = QVBoxLayout()
        user_input_layout = QVBoxLayout()
        user_input_upper_layout = QGridLayout()
        user_input_lower_layout = QGridLayout()

        self.current_cmd = ""
        self.cmd_list = CmdListWidget()
        cmd_list_layout.addWidget(self.cmd_list)

        text_box = QTextEdit()
        text_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        text_box.setFixedHeight(40)

        self.text_box = text_box
        self.add_cmd = AddCmdButton(text_box)

        # think about how to handle multiple input files
        input_video = IOButton(util.IOButtonEnum.INFILE)
        input_video.setText("Input")
        input_video.setFixedSize(100, 40)

        output_button = IOButton(util.IOButtonEnum.OUTFILE)
        output_button.setText("Output")
        output_button.setFixedSize(100, 40)

        run_button = QPushButton()
        run_button.setText("Run")
        run_button.setFixedSize(100, 40)

        user_input_upper_layout.addWidget(text_box,1,0)
        user_input_upper_layout.addWidget(self.add_cmd,0,1)

        user_input_lower_layout.addWidget(input_video,0,0)
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
        if e.type() == util.CmdChangedEventType:
            self.cmd_list.update_list()
            self.current_cmd = e.cmd_input
            self.text_box.setText(util.toCommand(self.current_cmd))
            return True
        elif e.type() == util.CmdTextEditedEventType:
            self.current_cmd[e.cmd_flag] = e.cmd_value
            cmd = util.toCommand(self.current_cmd)
            self.text_box.setText(cmd)
            print(cmd)
            return True
        elif e.type() == util.FileIOEventType:
            match e.io_type:
                case util.IOButtonEnum.INFILE:
                    self.current_cmd["-i"] = e.file_path
                case util.IOButtonEnum.OUTFILE:
                    self.current_cmd["out"] = e.file_path
                case util.IOButtonEnum.DIRECTORY:
                    pass
            self.text_box.setText(util.toCommand(self.current_cmd))
        return super().event(e)


class CmdListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        global processor
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # i need a way to convert cmds to json and json to cmds
        scroll_bar = QScrollBar(self)
        scroll_bar.setStyleSheet("background : gray;")
        self.setVerticalScrollBar(scroll_bar)
        self.update_list()

        self.itemClicked.connect(self.cmd_clicked)
    
    def update_list(self):
        self.clear()
        for command in processor.get_all_commands():
            item = QListWidgetItem(command)
            self.addItem(item)
    
    def cmd_clicked(self, item : QListWidgetItem):
        global processor
        current_cmd = {item.text() : processor.get_command(item.text())}
        QApplication.postEvent(window, util.CmdChangedEvent(current_cmd))


class AddCmdButton(QPushButton):
    def __init__(self, input_text_box : QTextEdit):
        super().__init__()
        self.geometry = QRect(20,20,10,10)
        self.clicked.connect(self.add_new_cmd)
        self.input_box = input_text_box
    
    def add_new_cmd(self):
        self.w = AddCmdWindow()
        self.w.show()


class AddCmdWindow(QWidget):
    def __init__(self):
        super().__init__()
        global processor
        layout = QVBoxLayout()

        label = QLabel("Edit and name command before adding\nCapture part of a value with [ ] brackets to create a variable")

        name_box = QTextEdit("New Command")
        name_box.setMaximumHeight(30)
        name_box.setMaximumWidth(120)
        name_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.name_edit_text = name_box

        edit_box = QTextEdit(util.toCommand(window.current_cmd))
        edit_box.setMaximumHeight(80)
        edit_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.cmd_edit_text = edit_box

        push_button = QPushButton()
        push_button.setText("Add Command")
        push_button.setMaximumHeight(50)
        push_button.setMaximumWidth(100)
        push_button.clicked.connect(self.on_click)

        layout.addWidget(label)
        layout.addWidget(name_box)
        layout.addWidget(edit_box)
        layout.addWidget(push_button)

        self.setLayout(layout)
     
    def on_click(self):
        global processor
        processor.add_command(self.name_edit_text.toPlainText(), self.cmd_edit_text.toPlainText())


class IOButton(QPushButton):
    def __init__(self, io_type : util.IOButtonEnum):
        super().__init__()
        self.io_type = io_type
        self.io_path = ""
        self.clicked.connect(self.get_io_func())

    def get_io_func(self):
        match self.io_type:
            case util.IOButtonEnum.INFILE:
                return self.browse_for_in_file
            case util.IOButtonEnum.DIRECTORY:
                return self.browse_for_directory
            case util.IOButtonEnum.OUTFILE:
                return self.browse_for_out_file
        
    def browse_for_directory(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select a Directory")

        if folder_path:
            self.io_path = folder_path
            QApplication.postEvent(window, util.FileIOEvent((self.file_path, self.io_type)))
            return folder_path
        return ""
    
    def browse_for_out_file(self):
        file_path = QFileDialog.getSaveFileName(self, "Save Output File", "", "Video Files (*.mp4);;All Files (*)")

        if file_path:
            self.io_path, _= file_path
            QApplication.postEvent(window, util.FileIOEvent((self.io_path, self.io_type)))
            return file_path
        return file_path

    def browse_for_in_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select a File","","All Files (*)")

        if file_path:
            self.io_path, _ = file_path
            QApplication.postEvent(window, util.FileIOEvent((self.io_path, self.io_type)))
            return file_path
        
        return ""
    

app = QApplication(sys.argv)

window = MainWindow()

app.exec()