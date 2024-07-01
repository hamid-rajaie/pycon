from PyQt5.QtGui import QColor, QFont, QStandardItem


class PyConStandardItem(QStandardItem):
    def __init__(
        self,
        channel_group_index: int,
        channel_group_comment: str,
        channel_index: int,
        text="",
        font_size=12,
        set_bold=False,
        color=QColor(0, 0, 0),
    ):
        super().__init__()
        fnt = QFont("Open Sans", font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        # self.setFont(fnt)
        self.setText(text)

        self.channel_group_index = channel_group_index
        self.channel_group_comment = channel_group_comment
        self.channel_index = channel_index
