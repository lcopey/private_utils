from typing import Dict, List, Union

from components import Modal, TableWithControls
from dash.html import Div

from private_utils.dash_components import BaseComponent, Style

# type definition for hinting
_dict_of_str = Dict[str, str]
_list_of_str = List[str]
_column_store = Dict[str, Union[_dict_of_str, _list_of_str]]


class MainPage(BaseComponent):
    """Main component."""

    def __init__(self, app, file_path: str, component_id: str = None):
        super().__init__(component_id=component_id, app=app)
        self.table = TableWithControls.from_file_path(component_id=self.generate_id('main_table'), app=app,
                                                      file_path=file_path,
                                                      include_total=True, editable=False)

        self.modal = Modal(component_id='modal')

    def layout(self):
        """Register layout."""
        return Div([self.table, self.modal],
                   style=Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem'))

    def register_callbacks(self):
        """Register callbacks."""
        pass
