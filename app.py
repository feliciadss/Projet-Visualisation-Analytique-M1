from flask import Flask, render_template, request
from view.map import build_map
from static.enumerations import genres

app = Flask(__name__)

# Page d'accueil
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

@app.route('/page4')
def page4():
    return render_template('page4.html')

if __name__ == '__main__':
    app.run(debug=True)
