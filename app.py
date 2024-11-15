from dash import Dash, html, dcc
import dash

# Initialisation de l'application avec support multipage
app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
