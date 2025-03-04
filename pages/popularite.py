from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import pycountry
from static.enumerations import genre_colors, flags
from data.data_manager import DataManager
import dash
import matplotlib.colors as mcolors

dash.register_page(__name__, path="/popularite", name="Popularité des genres")

# Données des festivals
festivals_path = "./static/festivals_europe.csv"
try:
    festivals_df = pd.read_csv(festivals_path)
except FileNotFoundError:
    festivals_df = pd.DataFrame()
    print(f"Erreur : Fichier festivals_europe.csv introuvable à {festivals_path}")

# Charger les données GeoJSON
geojson_path = "./static/custom.geo.json"
try:
    with open(geojson_path, "r", encoding="utf-8") as geojson_file:
        european_geojson = json.load(geojson_file)
except FileNotFoundError:
    european_geojson = None
    print(f"Erreur : Fichier custom.geo.json introuvable à {geojson_path}")


# Fonction pour convertir les codes ISO2 en ISO3
def convert_iso2_to_iso3(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code)
    if country:
        return country.alpha_3
    else:
        print(f"Code ISO2 non trouvé : {iso2_code}")
        return None
    
# Fonction pour foncer une couleur
def darken_color(color, factor=0.3):
    """
    Darken a given color by multiplying its RGB values by a factor.
    Factor should be between 0 (black) and 1 (no change).
    """
    rgb = mcolors.to_rgb(color)  # Convert to RGB format
    darker_rgb = tuple(c * factor for c in rgb)  # Reduce brightness
    return mcolors.to_hex(darker_rgb)  # Convert back to hex


# Ordre temporel des mois
MONTH_ORDER = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]


# Timeline des festivals
def create_festival_timeline(selected_genre):
    festivals_df["Mois"] = pd.Categorical(
        festivals_df["Mois"], categories=MONTH_ORDER, ordered=True
    )

    filtered_festivals = festivals_df[
        festivals_df["Genres musicaux"].str.contains(
            selected_genre, case=False, na=False
        )
    ]

    filtered_festivals = filtered_festivals.sort_values("Mois")

    fig_timeline = go.Figure()

    for month in filtered_festivals["Mois"].unique():
        month_festivals = filtered_festivals[filtered_festivals["Mois"] == month]
        for _, row in month_festivals.iterrows():
            # R du pays
            country_flag = flags.get(row["Pays"], "")

            hover_text = (
                f"Pays : {row['Pays']} {country_flag}<br>"
                f"Spectateurs : {row['Participants (approx)']}<br>"
                f"Prix moyen : {row['Prix moyen (€)']} €<br>"
                f"Genres : {row['Genres musicaux']}"
            )

            fig_timeline.add_trace(
                go.Scatter(
                    x=[month],
                    y=[row["Nom du festival"]],
                    mode="text",
                    marker=dict(size=10),
                    text=f"{row['Nom du festival']} {country_flag}",
                    hovertext=hover_text,
                    hoverinfo="text",
                    textfont=dict(size=14),
                    textposition="top center",
                    showlegend=False,
                )
            )

    fig_timeline.update_layout(
        title=f"Principaux festivals de {selected_genre.title()} en Europe sur une année",
        xaxis=dict(showgrid=False),
        yaxis=dict(
            title="Festival",
            visible=False,
            showticklabels=False,
            range=[-1, len(filtered_festivals)],
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        showlegend=False,
    )

    return fig_timeline


layout = html.Div(
    style={"backgroundColor": "black", "color": "white", "padding": "1%"},
    children=[
        # Titre principal
        html.H1(
            "Popularité des genres musicaux en Europe",
            style={"textAlign": "center", "color": "white"},
        ),
        # Sous-titre
        html.H3(
            "Découvrez la popularité de chaque genre à travers les pays européens.",
            style={"textAlign": "center", "color": "white", "fontWeight": "normal"},
        ),
        # Conteneur
        html.Div(
            style={
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "space-between",
                "alignItems": "center",
                "margin": "1%",
            },
            children=[
                # Bouton retour accueil
                html.Div(
                    style={
                        "position": "absolute",
                        "top": "30px",
                        "right": "30px",
                        "z-index": "1000",
                        "font-size": "40px",
                    },
                    children=[dcc.Link("🏠", href="/")],
                ),
                # Graphique en bulles (1/4 largeur)
                html.Div(
                    style={"flex": "2", "padding": "0%", "width": "100%", "overflow": "hidden"},
                    children=[
                        dcc.Graph(
                            id="bubble-genre-chart",
                            style={"height": "600px", "width": "100%"},
                        )
                    ],
                ),
                # Carte (3/4 largeur)
                html.Div(
                    style={"flex": "3", "padding": "0%", "width": "65%", "margin-bottom": "0"},
                    children=[
                        dcc.Graph(
                            id="map-graph", style={"height": "600px", "width": "100%"}
                        )
                    ],
                ),
            ],
        ),
        # Timeline des festivals
        html.Div(
            style={"padding": "0", "margin-top": "0", "width": "100%", "margin": "0 auto"},
            children=[dcc.Graph(id="festival-timeline", style={"height": "500px"})],
        ),
        # Pied de page
        html.Footer(
            html.Small(
                [
                    "Les données sont fournies par l' ",
                    html.A(
                        "API Spotify",
                        href="https://developer.spotify.com/documentation/web-api",
                        target="_blank",
                        style={"color": "white"},
                    ),
                ]
            ),
            style={
                "textAlign": "center",
                "padding": "10px",
                "backgroundColor": "black",
                "width": "100%",
                "fontSize": "12px",
                "color": "#999",
            },
        ),
    ],
)


@callback(
    [
        Output("bubble-genre-chart", "figure"),
        Output("map-graph", "figure"),
        Output("festival-timeline", "figure"),
    ],
    [Input("bubble-genre-chart", "clickData")],
)
def update_charts(click_data):
    data_manager = DataManager()

    genre_counts_df = data_manager.create_genre_count_dataframe()
    genre_counts_df["scaled_size"] = np.sqrt(genre_counts_df["total_count"])

    n_genres = len(genre_counts_df)
    grid_size = int(np.ceil(np.sqrt(n_genres)))
    genre_counts_df["x"] = np.tile(np.linspace(-1, 1, grid_size), grid_size)[:n_genres]
    genre_counts_df["y"] = np.repeat(np.linspace(-1, 1, grid_size), grid_size)[
        :n_genres
    ]
    genre_counts_df["x"] += np.random.uniform(low=-0.05, high=0.05, size=n_genres)
    genre_counts_df["y"] += np.random.uniform(low=-0.05, high=0.05, size=n_genres)

    selected_genre = "pop"
    if click_data:
        selected_genre = click_data["points"][0]["hovertext"]

    fig_bubble = px.scatter(
        genre_counts_df,
        x="x",
        y="y",
        size="scaled_size",
        color="genre",
        hover_name="genre",
        size_max=90,
        text="genre",
        color_discrete_map=genre_colors,
    )
    fig_bubble.update_traces(
        textposition="middle center",
        textfont=dict(color="black"),
        hovertemplate="",
        hoverinfo="none",
    )  # Nom du genre en noir au centre
    fig_bubble.update_layout(
        xaxis=dict(range=[-1.5, 1.5], visible=False),
        yaxis=dict(range=[-1.5, 1.5], visible=False),
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        showlegend=False,
    )

    df = data_manager.create_genre_popularity_by_country(selected_genre)
    df["total_popularity_percentile"] = df["total_popularity"].rank(pct=True)

    if df.empty:
        print(f"Aucune donnée disponible pour le genre {selected_genre}")
        return fig_bubble, go.Figure(), go.Figure()

    df["country"] = df["country"].apply(convert_iso2_to_iso3)  # conversion ios2 en ios3

    color_for_genre = genre_colors.get(selected_genre.lower(), "#ffffff")
    dark_color = darken_color(color_for_genre, factor=0.2)

    fig_map = px.choropleth(
        df,
        geojson=european_geojson,
        locations="country",
        featureidkey="properties.adm0_a3",
        color="total_popularity_percentile",
        color_continuous_scale=[[0, color_for_genre], [1, dark_color]],
        title=f"→ {selected_genre.title()}",
        labels={"total_popularity_percentile": "Popularité (%)", "country": "Pays"},
    )

    fig_map.update_geos(
        scope="europe",
        projection_type="equirectangular",
        showcoastlines=False,
        showland=True,
        center=dict(lat=51.9194, lon=19.1451),
        projection_scale=1,
        landcolor="white",
        bgcolor="black",
        visible=True,
        lonaxis=dict(range=[-50, 60]),
        lataxis=dict(range=[15, 85]),
    )

    fig_map.update_layout(
        title_font_size=20,
        autosize=True,
        geo=dict(showframe=False, showcoastlines=False),
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        margin={"r": 10, "t": 50, "l": 0, "b": 0},
        width=800,
        height=500,
        coloraxis_colorbar=dict(
            x=0.85, tickvals=[0.2, 0.4, 0.6, 0.8], title="Popularité (%)"
        ),
    )

    fig_timeline = create_festival_timeline(selected_genre)

    return fig_bubble, fig_map, fig_timeline
