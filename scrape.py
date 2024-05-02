from flask import Flask, render_template
import pandas as pd
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape top anime data from MyAnimeList
def scrape_top_anime():
    url = "https://myanimelist.net/topanime.php"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        anime_data = []
        anime_list = soup.find_all('tr', class_='ranking-list')
        for anime in anime_list:
            title = anime.find('div', class_='detail').find('a').text.strip()
            rating = float(anime.find('td', class_='score').text.strip())
            anime_data.append({'Title': title, 'Rating': rating})
        anime_df = pd.DataFrame(anime_data)
        return anime_df
    else:
        print("Failed to retrieve page content.")
        return None

# Function to generate insights from scraped anime data
def generate_insights(anime_df):
    if anime_df is not None:
        # Calculate additional insights
        average_rating = anime_df['Rating'].mean()
        highest_rated_anime = anime_df.loc[anime_df['Rating'].idxmax()]
        return average_rating, highest_rated_anime
    else:
        return None, None

# Route for the homepage
@app.route('/')
def index():
    # Scrape top anime data
    anime_df = scrape_top_anime()

    if anime_df is not None:
        # Generate insights
        average_rating, highest_rated_anime = generate_insights(anime_df)

        # Render DataFrame as HTML
        raw_data_html = anime_df.to_html(index=False)

        # Prepare summary stats
        summary_stats = anime_df.describe()

        # Render the index.html template with scraped data and insights
        return render_template('index.html', raw_data=raw_data_html, summary_stats=summary_stats,
                               average_rating=average_rating, highest_rated_anime=highest_rated_anime)
    else:
        return "Failed to retrieve data from MyAnimeList."

# Route for the insights page
@app.route('/insight')
def insights():
    # Scrape top anime data
    anime_df = scrape_top_anime()

    if anime_df is not None:
        # Generate insights
        average_rating, highest_rated_anime = generate_insights(anime_df)

        # Render the insight.html template with the calculated insights
        return render_template('insight.html', average_rating=average_rating, highest_rated_anime=highest_rated_anime)
    else:
        return "Failed to retrieve data from MyAnimeList."

if __name__ == '__main__':
    app.run(debug=True)
