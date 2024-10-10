from flask import Flask, render_template, request
from view.map import build_map
from static.enumerations import genres
from view.radar import build_radar
from view.barcharts import build_barcharts
from view.linear import build_linear_chart
from view.bubblechart import build_bubble_chart
from view.sankey_diagram import build_sankey_diagram


app = Flask(__name__)

@app.route('/')
@app.route('/', methods=['GET', 'POST'])
def index():
    selected_genre = None
    bubble_chart = None

    if request.method == 'POST':
        selected_genre = request.form.get('genre')  # Récupère le genre sélectionné dans le formulaire

        if selected_genre:
            bubble_chart = build_bubble_chart(selected_genre)  # Génère le diagramme en fonction du genre

    return render_template('index.html', genres=genres, bubble_chart=bubble_chart)


@app.route('/page1', methods=['GET', 'POST'])
def page1():
    selected_genre = None
    data_json = None

    if request.method == 'POST':
        selected_genre = request.form['genre']
        data_json = build_map(selected_genre) 
    return render_template('page1.html', genres=genres, selected_genre=selected_genre, data_json=data_json)


@app.route('/page2', methods=['GET', 'POST'])
def page2():
    selected_genres = None
    chart = None

    if request.method == 'POST':
        selected_genres = request.form.getlist('genres')

        if selected_genres:
            chart = build_linear_chart(selected_genres).to_html()
    
    return render_template('page2.html', genres=genres, selected_genres=selected_genres, chart=chart)

@app.route('/page3', methods=['GET', 'POST'])
def page3():
    selected_genres = None
    sankey = None

    if request.method == 'POST':
        selected_genres = request.form.getlist('genres')

        if selected_genres:
            sankey = build_sankey_diagram(selected_genres).to_html()
            if sankey:
                print("Sankey diagram HTML generated successfully.")
            else:
                print("Sankey diagram generation failed.")
    
    return render_template('page3.html', genres=genres, selected_genres=selected_genres, sankey=sankey)

@app.route('/page4', methods=['GET', 'POST'])
def page4():
    selected_genres = None
    radar_chart = None
    bar_charts = []

    if request.method == 'POST':
        selected_genres = request.form.getlist('genres')

        if selected_genres:
            radar_chart = build_radar(selected_genres).to_html()
            bar_charts = build_barcharts(selected_genres)

    return render_template('page4.html', genres=genres, radar_chart=radar_chart, bar_charts=bar_charts)


if __name__ == '__main__':
    app.run(debug=True)