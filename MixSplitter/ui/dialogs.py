from PySide6.QtWidgets import QInputDialog

def ask_name(parent):
    text, ok = QInputDialog.getText(parent, "Segment Name", "Name:")
    return text if ok else None