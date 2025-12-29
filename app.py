import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os
import time


# ================== VIDEO BACKGROUND ==================
def video_background():
    st.markdown(
        """
        <style>
        .video-bg {
            position: fixed;
            top: 0;
            left: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -1;
            opacity: 0.25;
            object-fit: cover;
        }

        .stApp {
            background: transparent;
        }
        </style>

        <video class="video-bg" autoplay loop muted>
            <source src="https://www.w3schools.com/howto/rain.mp4" type="video/mp4">
        </video>
        """,
        unsafe_allow_html=True
    )


# ✅ Call background
video_background()
# =====================================================


# --- Fetch poster using TMDb API (NETWORK-SAFE VERSION) ---
def fetch_poster(movie_id, retries=3):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=5705a1eff1ed14b8023af350f39ca9a5&language=en-US"

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

        except Exception:
            time.sleep(1)  # wait before retry

    # Final fallback if all retries fail
    return "https://via.placeholder.com/300x450?text=Poster+Unavailable"


# --- Load pickled data with Google Drive download ---
@st.cache_resource
def load_data():
    os.makedirs('Models', exist_ok=True)

    movies_path = 'Models/movies.pkl'
    similarity_path = 'Models/similarity.pkl'

    if not os.path.exists(similarity_path):
        with st.spinner('🔄 Downloading model from Google Drive...'):
            gdown.download(
                'https://drive.google.com/uc?id=1PfWPJjnPgjOVXbfz4_LFiphD4fUEClX6',
                similarity_path,
                quiet=False
            )

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

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# ================== STREAMLIT UI ==================
st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox(
    "Choose a movie:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    st.subheader("Top 5 Similar Movies:")
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i], use_container_width=True)
