'''
Function:
    Custom Components for MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from PyQt5.QtWidgets import QTableWidgetItem


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
