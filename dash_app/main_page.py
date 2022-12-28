from components import LinkedTable, Modal, TableWithControls
from dash.html import Details, Div, Summary

from private_utils.dash_components import BaseComponent, Style


class MainPage(BaseComponent):
    """Main component."""

    def __init__(self, app, file_path: str, component_id: str = None):
        super().__init__(component_id=component_id, app=app)
        self.first_table = (TableWithControls.
                            from_file_path(component_id=self.generate_id('main_table'),
                                           app=app,
                                           file_path=file_path,
                                           include_total=True,
                                           editable=True,
                                           style_as_list_view=False))
        self.linked_table = LinkedTable(component_id=self.generate_id('linked_table'),
                                        app=app,
                                        linked=self.first_table)

        self.modal = Modal(component_id='modal')

    def layout(self):
        """Register layout."""
        first = Details([Summary('Table', ), self.first_table], open=True)
        second = Details([Summary('Linked'), self.linked_table], open=True)
        return Div([first, second, self.modal],
                   style=Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem'))

    def register_callbacks(self):
        """Register callbacks."""
        pass
