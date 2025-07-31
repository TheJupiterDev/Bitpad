"""Bitpad - a Developer-focused text editor for notes, ideas, and inspiration."""

import json
import os
import sys
from i18n import lang, set_language
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QTabWidget, QWidget, QStatusBar, QVBoxLayout, QTextEdit, QInputDialog,
    QMessageBox, QFileDialog, QToolBar, QPushButton
)
from PySide6.QtGui import (QAction, QKeySequence, QTextCursor, QTextDocument, QIcon)
from PySide6.QtCore import QTimer, Qt, QPoint

from dialogs import FindReplaceDialog, FindDialog

set_language("en")

PERSISTENCE_FILE = os.path.expanduser("~/.bitpad_autosave.json")
BOOKMARKS_FILE = os.path.expanduser("~/.bitpad_bookmarks.json")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class BitPad(QMainWindow):
    def __init__(self):
        super().__init__()

        # ----- Window
        self.setWindowTitle(lang("window.title"))
        self.setGeometry(300, 300, 900, 600)
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))

        # ----- Menu Bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu(lang("menubar.file.title"))
        self.edit_menu = self.menu_bar.addMenu(lang("menubar.edit.title"))
        self.bookmarks_menu = self.menu_bar.addMenu(lang("menubar.bookmarks.title"))
        self.help_menu = self.menu_bar.addMenu(lang("menubar.help.title"))

        self.new_tab_action = QAction(lang("menubar.file.newtab"), self)
        self.save_action = QAction(lang("menubar.file.save"), self)
        self.save_as_action = QAction(lang("menubar.file.saveas"), self)
        self.open_action = QAction(lang("menubar.file.open"), self)
        self.exit_action = QAction(lang("menubar.file.exit"), self)
        self.about_action = QAction(lang("menubar.help.about"), self)
        self.undo_action = QAction(lang("menubar.edit.undo"), self)
        self.redo_action = QAction(lang("menubar.edit.redo"), self)
        self.find_action = QAction(lang("menubar.edit.find"), self)
        self.replace_action = QAction(lang("menubar.edit.replace"), self)
        self.add_bookmark_action = QAction(lang("menubar.bookmarks.add"))

        self.file_menu.addAction(self.new_tab_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.help_menu.addAction(self.about_action)

        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.find_action)
        self.edit_menu.addAction(self.replace_action)

        self.bookmarks_menu.addAction(self.add_bookmark_action)

        # ----- Bookmark Bar
        self.bookmarks_bar = QToolBar(lang("bookmarks.title"))
        self.bookmarks_bar.setMovable(False)

        list_add_icon = QIcon.fromTheme("list-add")
        self.new_tab_button = QPushButton()
        self.new_tab_button.setIcon(list_add_icon)
        self.new_tab_button.setFixedSize(30, 30)
        self.new_tab_button.setToolTip(lang("tabs.newtab.tooltip"))
        self.bookmarks_bar.addWidget(self.new_tab_button)

        self.bookmarks_bar.addSeparator()
        
        bookmark_icon = QIcon(resource_path("assets/bookmark.png"))
        self.add_bookmark_button = QAction(bookmark_icon, lang("bookmarks.bookmark_tab"), self)
        self.add_bookmark_button.setToolTip(lang("bookmarks.bookmark_tab"))
        self.add_bookmark_button.triggered.connect(self.add_bookmark)
        self.bookmarks_bar.addAction(self.add_bookmark_button)

        self.addToolBar(self.bookmarks_bar)

        self.bookmark_buttons = []

        # ----- Shortcuts
        self.new_tab_action.setShortcut(QKeySequence.StandardKey.New)     # Ctrl+N
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)       # Ctrl+O
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)       # Ctrl+S
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)  # Ctrl+Shift+S
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)       # Ctrl+Q
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)       # Ctrl+Z
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)       # Ctrl+Y
        self.find_action.setShortcut(QKeySequence.StandardKey.Find)       # Ctrl+F
        self.replace_action.setShortcut(QKeySequence.StandardKey.Replace) # Ctrl+H

        # ----- Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(self.rename_tab)

        self.add_new_tab(lang("tabs.default_title"))

        # ----- Central Widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # ----- Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(lang("status.ready"))

        # ----- Bookmarks
        self.bookmarks = self.load_bookmarks()
        self.update_bookmarks_bar()

        # ----- Persistence
        self.setup_persistence()

        # ----- Connections
        self.new_tab_action.triggered.connect(lambda: self.add_new_tab(lang("tabs.default_title")))
        self.save_action.triggered.connect(self.save_current_tab)
        self.save_as_action.triggered.connect(self.save_current_tab_as)
        self.open_action.triggered.connect(self.open_file)
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self.about_dialog)
        self.undo_action.triggered.connect(self.undo_current_tab)
        self.redo_action.triggered.connect(self.redo_current_tab)
        self.find_action.triggered.connect(self.show_find_dialog)
        self.replace_action.triggered.connect(self.show_replace_dialog)
        self.add_bookmark_action.triggered.connect(self.add_bookmark)
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab(lang("tabs.default_title")))

    def add_new_tab(self, title, content="", insert_index=None):
        editor = QTextEdit()
        editor.setPlainText(content)

        if insert_index is None:
            index = self.tabs.count()
            self.tabs.insertTab(index, editor, title)
        else:
            index = insert_index
            self.tabs.insertTab(insert_index, editor, title)

        self.tabs.setCurrentIndex(index)
        return index

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            self.rebuild_tab_file_paths()
    
    def rename_tab(self, index):
        if index != -1:
            current_title = self.tabs.tabText(index)
            new_title, ok = QInputDialog.getText(self, lang("dialog.rename_tab.title"), lang("dialog.rename_tab.text"), text=current_title)
            if ok and new_title.strip():
                self.tabs.setTabText(index, new_title.strip())
    
    def about_dialog(self):
        QMessageBox.about(self, lang("dialog.about.title"), lang("dialog.about.text"))

    def closeEvent(self, event):
        self.autosave()
        event.accept()

    def setup_persistence(self):
        self.tab_file_paths = {}
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(5000) # 5 seconds

        self.load_persistent_tabs()
    
    def autosave(self):
        data = []

        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            title = self.tabs.tabText(i)
            content = editor.toPlainText()
            path = self.tab_file_paths.get(i)
            data.append({"title": title, "content": content, "path": path})
        
        try:
            with open(PERSISTENCE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
        
        except:
            pass
            # TODO: Add logging!

    def load_persistent_tabs(self):
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        
        if not os.path.exists(PERSISTENCE_FILE):
            self.add_new_tab(lang("tabs.default_title"))
            return
        
        try:
            with open(PERSISTENCE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not data:
                self.add_new_tab(lang("tabs.default_title"))
                return
            
            for tab in data:
                title = tab.get("title", lang("tabs.default_title"))
                content = tab.get("content", "")
                path = tab.get("path")
                self.add_new_tab(title, content)
                self.tab_file_paths[self.tabs.count() - 1] = path
        
        except Exception:
            self.add_new_tab(lang("tabs.default_title"))
            # TODO: Add logging!

    def rebuild_tab_file_paths(self):
        new_paths = {}
        for i in range(self.tabs.count()):
            new_paths[i] = self.tab_file_paths.get(i)
        self.tab_file_paths = new_paths

    def save_current_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index == -1:
            return
        
        file_path = self.tab_file_paths.get(current_index)

        if file_path:
            self.save_to_file(current_index, file_path)
        else:
            self.save_current_tab_as()
    
    def save_current_tab_as(self):
        current_index = self.tabs.currentIndex()
        if current_index == -1:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            lang("dialog.save.title"),
            "",
            lang("dialog.save.filter")
        )

        if file_path:
            self.save_to_file(current_index, file_path)
            self.tab_file_paths[current_index] = file_path

            filename = os.path.basename(file_path)
            self.tabs.setTabText(current_index, filename)

    def save_to_file(self, tab_index, file_path):
        try:
            editor = self.tabs.widget(tab_index)
            content = editor.toPlainText()

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            filename = os.path.basename(file_path)
            self.status.showMessage(lang("status.saved").format(filename=filename))

        except Exception as e:
            #TODO: add logging!
            QMessageBox.warning(self, lang("error.save.title"), lang("error.save.message").format(error=str(e)))

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            lang("dialog.open.title"), 
            "", 
            lang("dialog.save.filter")
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                tab_index = self.add_new_tab(filename, content)
                self.tab_file_paths[tab_index] = file_path
                
                self.status.showMessage(lang("status.opened").format(filename=filename))
            except Exception as e:
                QMessageBox.warning(self, lang("error.open.title"), lang("error.open.message").format(error=str(e)))

    def undo_current_tab(self):
        current_editor = self.tabs.currentWidget()
        if current_editor:
            current_editor.undo()

    def redo_current_tab(self):
        current_editor = self.tabs.currentWidget()
        if current_editor:
            current_editor.redo()
    
    def show_find_dialog(self):
        dialog = FindDialog(self)
        dialog.exec()

    def show_replace_dialog(self):
        dialog = FindReplaceDialog(self)
        dialog.exec()
    
    def find_text(self, text, case_sensitive=False, whole_words=False):
        current_editor = self.tabs.currentWidget()
        if not current_editor or not text:
            return False
        
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords
        
        return current_editor.find(text, flags)

    def replace_text(self, find_text, replace_text, case_sensitive=False, whole_words=False):
        current_editor = self.tabs.currentWidget()
        if not current_editor:
            return False
        
        cursor = current_editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            if (case_sensitive and selected == find_text) or (not case_sensitive and selected.lower() == find_text.lower()):
                cursor.insertText(replace_text)
                return True
        return False

    def replace_all(self, find_text, replace_text, case_sensitive=False, whole_words=False):
        current_editor = self.tabs.currentWidget()
        if not current_editor or not find_text:
            return 0
        
        cursor = current_editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        current_editor.setTextCursor(cursor)
        
        count = 0
        while self.find_text(find_text, case_sensitive, whole_words):
            if self.replace_text(find_text, replace_text, case_sensitive, whole_words):
                count += 1
            else:
                break
        
        return count

    def save_bookmarks(self):
        try:
            with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.bookmarks, f)
        except Exception:
            pass

    def load_bookmarks(self):
        if not os.path.exists(BOOKMARKS_FILE):
            return []
        try:
            with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def add_bookmark(self):
        current_index = self.tabs.currentIndex()
        if current_index == -1:
            return

        editor = self.tabs.widget(current_index)
        content = editor.toPlainText()
        title = self.tabs.tabText(current_index)
        file_path = self.tab_file_paths.get(current_index)

        name, ok = QInputDialog.getText(self, "Add Bookmark", "Bookmark name:", text=title)
        if ok and name.strip():
            self.bookmarks.append({
                "name": name.strip(),
                "title": title,
                "content": content,
                "file_path": file_path
            })
            self.save_bookmarks()
            self.update_bookmarks_bar()

    def update_bookmarks_bar(self):
        for action in self.bookmark_buttons:
            self.bookmarks_bar.removeAction(action)
        self.bookmark_buttons = []

        for i, bookmark in enumerate(self.bookmarks):
            action = QAction(bookmark["name"], self)

            def handle_triggered(_, b=bookmark):
                self.open_bookmarked_file(b)

            def handle_right_click(_, index=i):
                self.remove_bookmark_dialog(index)

            action.triggered.connect(handle_triggered)
            self.bookmarks_bar.addAction(action)
            self.bookmark_buttons.append(action)

            widget = self.bookmarks_bar.widgetForAction(action)
            if widget:
                widget.setContextMenuPolicy(Qt.CustomContextMenu)
                widget.customContextMenuRequested.connect(lambda _, i=i: self.remove_bookmark_dialog(i))
    
    def remove_bookmark_dialog(self, index):
        bookmark = self.bookmarks[index]
        reply = QMessageBox.question(
            self,
            "Remove Bookmark",
            f"Remove bookmark '{bookmark['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.bookmarks[index]
            self.save_bookmarks()
            self.update_bookmarks_bar()

    def open_bookmarked_file(self, bookmark):
        file_path = bookmark.get("file_path")
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                tab_index = self.add_new_tab(filename, content)
                self.tab_file_paths[tab_index] = file_path
                
                return
            except Exception:
                # File couldn't be read, fall back to stored content
                pass
        
        # Fallback: use stored content
        index = self.add_new_tab(bookmark["title"], bookmark["content"])

if __name__ == '__main__':
    app = QApplication([])
    window = BitPad()
    window.show()
    app.exec()