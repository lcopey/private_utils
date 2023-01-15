from typing import List

from dash import Input, Output, State, ctx, dcc, html, no_update
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from text import words

from private_utils.dash_components import BaseComponent, DashApp


class SelectionPanel(BaseComponent):
    def __init__(self, app: DashApp, component_id: str, options: List[str], page_size: int = 10):
        super().__init__(component_id=component_id, app=app)
        column_id = "option"
        records = [{column_id: word, "id": n} for n, word in enumerate(options)]
        self.selectable = DataTable(
            data=records,
            columns=[{"name": "selectable", "id": column_id}],
            style_as_list_view=True,
            filter_action="native",
            row_selectable="multi",
            page_current=0,
            page_size=page_size,
        )

        button_style = {"position": "relative", "top": "2.6em", "zIndex": 1}
        self.select_all = html.Button("Select all", style=button_style, n_clicks=0)
        self.select_none = html.Button("Select none", style=button_style, n_clicks=0)
        self.order = dcc.Store(id=self.generate_id('order'), data=[])
        self.selected = DataTable(
            columns=[{"name": "selected", "id": column_id}],
            filter_action="native",
            page_current=0,
            page_size=page_size
        )
        self.up = html.Button('up', style=button_style, n_clicks=0)
        self.down = html.Button('down', style=button_style, n_clicks=0)

    def layout(self):
        table_style = {"position": "relative", "top": "-1.3em"}
        layout = html.Div(
            [
                html.Div(
                    [
                        self.select_all,
                        self.select_none,
                        html.Div(
                            self.selectable,
                            style=table_style,
                        ),
                    ]
                ),
                html.Div(
                    [
                        self.up,
                        self.down,
                        html.Div(
                            [self.selected,
                             self.order],
                            style=table_style
                        )
                    ]
                )
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)"},
        )
        return layout

    def register_callbacks(self):
        @self.app.callback(
            Output(self.selectable, "selected_rows"),
            Input(self.select_all, "n_clicks"),
            Input(self.select_none, "n_clicks"),
            State(self.selectable, "data"),
        )
        def on_button_triggered(all_clicked, none_clicked, records):
            if ctx.triggered_id == self.select_all.id:
                return [n for n, _ in enumerate(records)]
            if ctx.triggered_id == self.select_none.id:
                return []
            raise PreventUpdate

        @self.app.callback(
            Output(self.selectable, "style_data_conditional"),
            Output(self.selected, "data"),
            Input(self.selectable, "derived_viewport_selected_row_ids"),
            State(self.selectable, "selected_rows"),
            State(self.selectable, "data"),
        )
        def on_selected(viewport_selected, selected, records,):
            if viewport_selected is None:
                style_data_conditional = no_update
            else:
                style_data_conditional = [
                    {
                        "if": {"filter_query": "{{id}} ={}".format(i)},
                        'backgroundColor': '#0074D9',
                        'color': 'white'
                    }
                    for i in viewport_selected
                ]
            if selected:
                selected_records = []
                for row in selected:
                    selected_records.append(records[row])
            else:
                selected_records = []

            return style_data_conditional, selected_records


app = DashApp()
selection = SelectionPanel(app=app, component_id='selection', options=words)

app.layout = selection

if __name__ == "__main__":
    app.run_server(debug=True)
