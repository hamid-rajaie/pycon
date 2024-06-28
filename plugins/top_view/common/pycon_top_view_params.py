from data_sources.pycon_data_source import PyConDataSource


class PyConTopViewParams:

    def __init__(self, pycon_data_source: PyConDataSource) -> None:

        self.pycon_data_source: PyConDataSource = pycon_data_source
