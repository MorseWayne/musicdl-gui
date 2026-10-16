'''
Function:
    Custom Components for MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import re
from PyQt5.QtWidgets import QTableWidgetItem


def size_value(text):
    match = re.fullmatch(r'\s*([\d.]+)\s*([KMGT]?I?B)?\s*', str(text), re.IGNORECASE)
    if not match:
        return 0
    try:
        unit = (match.group(2) or 'B').upper().replace('I', '')
        return float(match.group(1)) * 1024 ** ['B', 'KB', 'MB', 'GB', 'TB'].index(unit)
    except ValueError:
        return 0


def duration_value(text):
    try:
        value = 0
        for part in str(text).split(':'):
            value = value * 60 + float(part)
        return value
    except ValueError:
        return 0


class SortableTableWidgetItem(QTableWidgetItem):
    """
    Custom table widget item that supports proper sorting
    by maintaining both display text and sort value
    """
    def __init__(self, text, sort_value=None):
        """
        Initialize sortable table item
        
        Args:
            text (str): Display text
            sort_value: Value used for sorting (defaults to text if not provided)
        """
        super().__init__(text)
        self.sort_value = sort_value if sort_value is not None else text

    def __lt__(self, other):
        """
        Compare items for sorting
        
        Args:
            other: Another table item to compare with
            
        Returns:
            bool: True if this item is less than the other
        """
        if isinstance(other, SortableTableWidgetItem):
            try:
                return self.sort_value < other.sort_value
            except TypeError:
                return super().__lt__(other)
        return super().__lt__(other)
