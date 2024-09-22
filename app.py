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
    df_genres = get_genre_data_for_map()

    # Générer la carte avec la fonction build_map
    fig = build_map(df_genres)
    
    # Convertir la carte en HTML pour l'afficher dans le template
    plot_html = fig.to_html(full_html=False)
    
    # Afficher la carte sur la page
    return render_template('page1.html', plot=plot_html)


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
