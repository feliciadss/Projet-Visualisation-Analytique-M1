from flask import Flask, render_template, request
from view.map import build_map
from static.enumerations import genres
from view.spider import create_spider_chart

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1', methods=['GET', 'POST'])
def page1():
    selected_genre = None
    data_json = None

    if request.method == 'POST':
        selected_genre = request.form['genre']
        data_json = build_map(selected_genre) 
    return render_template('page1.html', genres=genres, selected_genre=selected_genre, data_json=data_json)


@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/page3')
def page3():
    return render_template('page3.html')

@app.route('/page4', methods=['GET', 'POST'])
def page4():
    selected_genres = None
    spider_chart = None

    if request.method == 'POST':
        selected_genres = request.form.getlist('genres')

        if selected_genres:
            # Créer la spider chart avec les genres sélectionnés
            spider_chart = create_spider_chart(selected_genres).to_html()
            print(spider_chart.head())

    return render_template('page4.html', genres=genres, spider_chart=spider_chart)

if __name__ == '__main__':
    app.run(debug=True)
