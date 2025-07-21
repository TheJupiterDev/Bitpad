# Bitpad

A developer-focused text editor for notes, ideas, and inspiration built with PySide6.

## Features

### Core Functionality
- **Tabbed Interface** - Work with multiple documents simultaneously
- **Auto-save** - Your work is automatically saved every 5 seconds
- **Session Persistence** - Tabs and content are restored when you restart the app
- **File Operations** - Open, save, and save-as .txt files
- **Tab Management** - Rename tabs by double-clicking, close with X button

### Text Editing
- **Undo/Redo** - Full undo/redo support with Ctrl+Z/Ctrl+Y
- **Find & Replace** - Search and replace text with options for case sensitivity and whole words
- **Keyboard Shortcuts** - Standard shortcuts for all common operations

### User Experience
- **Clean Interface** - Minimal, distraction-free design
- **Status Bar** - Shows current status and operation feedback
- **Internationalization** - Built-in support for multiple languages

## Requirements

- Python 3.7+
- PySide6
- Custom i18n module (for internationalization)

## Installation

1. Clone or download this repository
2. Install PySide6:
```bash  
pip install PySide6
```
3. Run the application:
```bash
python main.py
```
## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New Tab | Ctrl+N |
| Open File | Ctrl+O |
| Save | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Find | Ctrl+F |
| Find & Replace | Ctrl+H |
| Exit | Ctrl+Q |

## File Structure
```
bitpad/
├── main.py           # Main application file
├── i18n.py          # Internationalization module
├── lang/            # Language files
│   └── en.json      # English translations
└── README.md        # This file
```
## Auto-save & Persistence

Bitpad automatically saves your work in two ways:

1. **Auto-save**: Every 5 seconds, all tab content is saved to `~/.bitpad_autosave.json`
2. **Session Persistence**: When you restart Bitpad, all your tabs and content are restored exactly as you left them

This means you never lose your work, even if you forget to manually save or the application closes unexpectedly.

## Language Support

Bitpad supports internationalization through JSON language files. Currently includes:

- English (en)

To add a new language, create a new JSON file in the `lang/` directory following the same structure as `en.json`.

## Find & Replace

The Find & Replace feature supports:

- **Case Sensitive Search** - Match exact letter case
- **Whole Words Only** - Match complete words instead of partial matches  
- **Replace All** - Replace every occurrence in the document at once
- **Non-modal Dialogs** - Keep the dialog open while working with your text

## Contributing

This is a simple, focused text editor. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This app complies with the MIT License.

## Version History

### Version 1.0
- Initial release
- Tabbed interface with auto-save
- File operations (open, save, save as)
- Undo/redo functionality
- Find and replace
- Keyboard shortcuts
- Session persistence
- Internationalization support

---

**Bitpad** - Simple. Fast. Reliable.