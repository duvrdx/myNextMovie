from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import textwrap as twp
from PIL import Image, ImageDraw, ImageFont

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
    
    def create_table(self, df):
        fig = plt.figure(figsize=(8, 8), dpi=300)
        ax = plt.subplot()
        ncols = len(df.columns)
        nrows = df.shape[0]
        ax.set_xlim(0, ncols + 1)
        ax.set_ylim(0, nrows + 1)
        positions = [0.25] + list(range(2, ncols + 1))
        columns = df.columns
        # Add table's main text
        for i in range(nrows):
            for j, column in enumerate(columns):
                if j == 0:
                    ha = 'left'
                else:
                    ha = 'center'
                text_label = f'{df[column].iloc[i]}'
                weight = 'normal'
                ax.annotate(
                    xy=(positions[j], i + .5),
                    text=text_label,
                    ha=ha,
                    va='center',
                    weight=weight
                )
        # Add column names
        for index, c in enumerate(columns):
            if index == 0:
                ha = 'left'
            else:
                ha = 'center'
            ax.annotate(
                xy=(positions[index], nrows + .25),
                text=c,
                ha=ha,
                va='bottom',
                weight='bold'
            )
        # Add dividing lines
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [nrows, nrows], lw=1.5, color='black', marker='', zorder=4)
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], lw=1.5, color='black', marker='', zorder=4)
        for x in range(1, nrows):
            ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [x, x], lw=1.15, color='gray', ls=':', zorder=3, marker='')
        ax.set_axis_off()
        # Salve a figura em um buffer de bytes
        img_buffer = BytesIO()
        plt.savefig(img_buffer, dpi=300, transparent=True, bbox_inches='tight')
        img_buffer.seek(0)
        return img_buffer

    def suggest_movies(self, title) -> str:
        table_data = []


        suggestions = self.dataset[self.dataset["primaryTitle"].str.contains(title, case=False, regex=False)].sort_values(by=["numVotes"], ascending=False)
        
        if not suggestions.empty:
            pair = zip(suggestions["primaryTitle"], suggestions["startYear"])
            for pair in list(zip(suggestions["primaryTitle"], suggestions["startYear"]))[0:16]:
                table_data.append({"Title": twp.fill(pair[0], 40), "Year": pair[1]})

            
            # Crie um DataFrame do Pandas a partir dos dados da tabela
            df = pd.DataFrame(table_data)
            df = df[::-1]
            
            return self.create_table(df)

        else:
            return None

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