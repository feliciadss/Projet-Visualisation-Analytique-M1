from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from view.accueil import home_layout, register_callbacks


app = Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname is None:
        return home_layout
    else:
        return html.Div("Page non trouvée", style={'color': 'white', 'textAlign': 'center', 'marginTop': '50px'})

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
