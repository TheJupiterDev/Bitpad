from i18n import lang, set_language
from PySide6.QtWidgets import QVBoxLayout, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox

set_language("en")

class FindDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(lang("dialog.find.title"))
        self.setModal(False)
        
        layout = QVBoxLayout()
        
        # Find input
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel(lang("dialog.find.text")))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Options
        self.case_sensitive = QCheckBox(lang("dialog.find.case_sensitive"))
        self.whole_words = QCheckBox(lang("dialog.find.whole_words"))
        layout.addWidget(self.case_sensitive)
        layout.addWidget(self.whole_words)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.find_btn = QPushButton(lang("dialog.find.find_next"))
        self.close_btn = QPushButton(lang("dialog.find.close"))
        button_layout.addWidget(self.find_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connections
        self.find_btn.clicked.connect(self.find_next)
        self.close_btn.clicked.connect(self.close)
        self.find_input.returnPressed.connect(self.find_next)
        
    def find_next(self):
        text = self.find_input.text()
        found = self.parent.find_text(
            text, 
            self.case_sensitive.isChecked(), 
            self.whole_words.isChecked()
        )
        if not found and text:
            self.parent.status.showMessage(lang("status.not_found"))

class FindReplaceDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(lang("dialog.replace.title"))
        self.setModal(False)
        
        layout = QVBoxLayout()
        
        # Find input
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel(lang("dialog.find.text")))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Replace input
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel(lang("dialog.replace.text")))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Options
        self.case_sensitive = QCheckBox(lang("dialog.find.case_sensitive"))
        self.whole_words = QCheckBox(lang("dialog.find.whole_words"))
        layout.addWidget(self.case_sensitive)
        layout.addWidget(self.whole_words)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.find_btn = QPushButton(lang("dialog.find.find_next"))
        self.replace_btn = QPushButton(lang("dialog.replace.replace"))
        self.replace_all_btn = QPushButton(lang("dialog.replace.replace_all"))
        self.close_btn = QPushButton(lang("dialog.find.close"))
        
        button_layout.addWidget(self.find_btn)
        button_layout.addWidget(self.replace_btn)
        button_layout.addWidget(self.replace_all_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connections
        self.find_btn.clicked.connect(self.find_next)
        self.replace_btn.clicked.connect(self.replace_current)
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.close_btn.clicked.connect(self.close)
        self.find_input.returnPressed.connect(self.find_next)
        
    def find_next(self):
        text = self.find_input.text()
        found = self.parent.find_text(
            text, 
            self.case_sensitive.isChecked(), 
            self.whole_words.isChecked()
        )
        if not found and text:
            self.parent.status.showMessage(lang("status.not_found"))
    
    def replace_current(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        replaced = self.parent.replace_text(
            find_text, 
            replace_text,
            self.case_sensitive.isChecked(), 
            self.whole_words.isChecked()
        )
        if replaced:
            self.find_next()  # Find next occurrence
    
    def replace_all(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        count = self.parent.replace_all(
            find_text, 
            replace_text,
            self.case_sensitive.isChecked(), 
            self.whole_words.isChecked()
        )
        self.parent.status.showMessage(lang("status.replaced").format(count=count))