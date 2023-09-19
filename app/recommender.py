import pandas as pd
import prettytable as pt

class Recommender():
    def __init__(self, model, dataset, features) -> None:
        self.model = model
        self.dataset = dataset
        self.features = features

        self.dataset["startYear"] = pd.to_numeric(self.dataset["startYear"], errors="coerce")
        self.dataset["startYear"] = self.dataset["startYear"].fillna(0).astype(int)

    def __truncate_text(self, text, max_length):
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        else:
            return text

    def suggest_movies(self, title) -> str:
        table = pt.PrettyTable(['Titulo', 'Ano'])
        table.align['Ano'] = 'l'
        table.align['Titulo'] = 'l'

        suggestions = self.dataset[self.dataset["primaryTitle"].str.contains(title, case=False, regex=False)].sort_values(by=["numVotes"], ascending=False)
        
        if not suggestions.empty:
            pair = zip(suggestions["primaryTitle"], suggestions["startYear"])
            for pair in list(zip(suggestions["primaryTitle"], suggestions["startYear"]))[0:16]:
                table.add_row([f"{self.__truncate_text(pair[0], 20)}",f"{pair[1]}"])        
            return f'```{table}```'
        else:
            return ""

    def is_in_movie(self, title, year) -> bool:
        target = self.dataset[(self.dataset["primaryTitle"].str.lower() == title.lower()) & (self.dataset["startYear"] == year)]
        if not target.empty:
            return True
        return False

    def recommendMovie(self, title, year, num_movies) -> list:
        recommendations = []

        target_index = self.dataset[(self.dataset["primaryTitle"].str.lower() == title.lower()) & (self.dataset["startYear"] == year)].index[0]
        distances, neighbors = self.model.kneighbors([self.features[target_index]])

        for index in neighbors[0][1:num_movies]:
            recommendations.append({
                "movie": self.__truncate_text(self.dataset.iloc[index]["primaryTitle"], 35),
                "year": self.dataset.iloc[index]["startYear"]
            })

        return recommendations