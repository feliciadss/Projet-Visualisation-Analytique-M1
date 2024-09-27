from flask import Flask, render_template
from view.map import build_map 
from data.data_manager import get_genre_data_for_map

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1')
def page1():
    # Récupérer les données pour la carte de chaleur
    df = get_genre_data_for_map()

    # Convertir les données en JSON pour les passer à la page HTML
    data_json = df.to_json(orient='records')
    
    # Renvoyer le template avec les données
    return render_template('page1.html', data_json=data_json)



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
