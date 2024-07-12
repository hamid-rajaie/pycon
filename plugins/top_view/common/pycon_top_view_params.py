from data_sources.pycon_data_source_base import PyConDataSourceBase


class PyConTopViewParams:

    def __init__(self, pycon_data_source: PyConDataSourceBase) -> None:

        self.pycon_data_source: PyConDataSourceBase = pycon_data_source
