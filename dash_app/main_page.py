from components import ApiResultsStore, LinkedTable, Modal, TableWithControls
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
                                           style_as_list_view=False,
                                           is_open=True))
        self.api_store = ApiResultsStore(component_id=self.generate_id('api'),
                                         app=app,
                                         source_control=self.first_table.table,
                                         source_property='data',
                                         preprocess=self.first_table.converter.records_to_dict_of_dict,
                                         postprocess=self.first_table.converter.dict_of_dict_to_records)
        self.linked_table = LinkedTable(component_id=self.generate_id('linked_table'),
                                        app=app,
                                        column_source_control=self.first_table.table,
                                        column_source_property='columns',
                                        data_source_control=self.api_store.store,
                                        data_source_property='data',
                                        style_cell_conditional=self.first_table.table.style_cell_conditional)

        self.modal = Modal(component_id='modal')

    def layout(self):
        """Register layout."""
        hidden = Div([self.api_store])
        first = Details([Summary('Table', ), self.first_table], open=True)
        second = Details([Summary('Linked'), self.linked_table], open=True)
        return Div([first, second, hidden, self.modal],
                   style=Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem'))

    def register_callbacks(self):
        """Register callbacks."""
        pass
