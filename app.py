import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os


# --- Fetch poster using TMDb API ---
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=5705a1eff1ed14b8023af350f39ca9a5&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data['poster_path']
        full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return full_path
    except Exception as e:
        print(f"Error fetching poster for movie_id={movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=No+Image"


# --- Load pickled data with Google Drive download ---
@st.cache_resource
def load_data():
    movies_path = 'Models/movies.pkl'
    similarity_path = 'Models/similarity.pkl'

    # Download similarity.pkl from Drive (movies.pkl is already in GitHub)
    if not os.path.exists(similarity_path):
        with st.spinner('🔄 Downloading model from Google Drive...'):
            gdown.download('https://drive.google.com/uc?id=1PfWPJjnPgjOVXbfz4_LFiphD4fUEClX6', similarity_path,
                           quiet=False)

    movies = pickle.load(open(movies_path, 'rb'))
    similarity = pickle.load(open(similarity_path, 'rb'))
    return movies, similarity


movies, similarity = load_data()


# --- Recommend similar movies ---
def recommend(movie):
    if movie not in movies['title'].values:
        return ["Movie not found"], [""]

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# --- Streamlit UI ---
st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox("Choose a movie:", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    st.subheader("Top 5 Similar Movies:")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            if posters[i]:
                st.image(posters[i])
            else:
                st.write("Image not available")
