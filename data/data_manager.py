import pandas as pd
from data.get_data import get_data_from_mongodb  # Récupération des données brutes

import pandas as pd

def clean_genre(genre):
    """
    Simplifie les genres pour éviter les sous-genres ou des termes comme 'Albanian pop'.
    Par exemple, 'Albanian pop' deviendra 'pop'.
    """
    if isinstance(genre, list):
        return [g.split()[0].lower() for g in genre]  # Récupérer le mot principal du genre
    else:
        return genre.split()[0].lower() if isinstance(genre, str) else None

def get_genre_data_for_map():
    data = {
        'iso_a3': ['FRA', 'DEU', 'ITA', 'ESP', 'GBR', 'POL', 'SWE', 'NOR', 'DNK', 'BEL'],
        'popularity': [75, 60, 55, 65, 80, 50, 70, 45, 60, 85]
    }
    df_fictif = pd.DataFrame(data)
    return df_fictif
