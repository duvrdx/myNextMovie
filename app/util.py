from recommender import Recommender
import pandas as pd

def suggest_movies(title, year, movies_df) -> list:
    suggestions = movies_df[movies_df["title"].str.contains(title, case=False, regex=False)]
    print(suggestions)
    return suggestions

def is_in_movie(title, year, movies_df) -> bool:
    if movies_df[(movies_df['title'] == title) & (movies_df['startYear'] == year)]:
        return True
    return False

def recommendMovie(modelPath, title, year, num_movies) -> list:
    recommender = Recommender(modelPath)
    return recommender.recommendMovies(title, year, num_movies)
