import streamlit as st
import requests
import datetime
import pickle

def fetch_movie_info(movie_id):
     url = "https://api.themoviedb.org/3/movie/{}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US".format(movie_id)
     data=requests.get(url)
     data=data.json()
     poster_path = data['poster_path']
     vote_average = data['vote_average']
     release_date = data['release_date']
     full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
     return full_path, vote_average, release_date

def get_movie_genre(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    response = requests.get(url)
    data = response.json()
    genres = [genre['name'] for genre in data['genres']]
    return genres

movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
movies_list = movies['title'].values

st.header("Personalized Movie Recommendation System\n")

def movie_poster(image_urls, height=200):
    num_images = len(image_urls)
    num_columns = 5

    num_rows = (num_images + num_columns - 1) // num_columns

    for i in range(num_rows):
        row_images = image_urls[i * num_columns: (i + 1) * num_columns]
        st.write("\n")
        with st.expander(f"Made for you {i+1}"):
            cols = st.columns(len(row_images))
            for j, url in enumerate(row_images):
                cols[j].image(url, use_column_width=True)

imageUrls = []
recommended_ids = []

selectvalue = st.selectbox('Select a movie: ', movies_list)

def recommend(movie):
    global recommended_ids
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
    recommend_movie=[]
    recommend_poster=[]
    recommend_rating=[]
    recommend_year=[]
    recommended_ids = []
    for i in distance[1:11]:
        movies_id=movies.iloc[i[0]].id
        movie_info = fetch_movie_info(movies_id)
        recommended_ids.append(movies_id)
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(movie_info[0])
        recommend_rating.append(movie_info[1])
        recommend_year.append(datetime.datetime.strptime(movie_info[2], "%Y-%m-%d").year)
    return recommend_movie, recommend_poster, recommend_rating, recommend_year

recommend(selectvalue)

for movie_id in recommended_ids:
    movie_info = fetch_movie_info(movie_id)
    imageUrls.append(movie_info[0])
movie_poster(imageUrls)

if st.button("Show Recommend"):
    movie_name, movie_poster, movie_rating, movie_year = recommend(selectvalue)
    num_movies = min(10, len(movie_name))  
    num_columns = 2  

    for i in range(0, num_movies, num_columns):
        cols = st.columns(num_columns)
        for j in range(num_columns):
            movie_index = i + j
            if movie_index < num_movies:
                with cols[j]:
                    st.markdown(
                        f"""
                        <style>
                        .hover:hover {{
                            filter: brightness(85%);
                            transition: 0.3s;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    st.image(movie_poster[movie_index], use_column_width=True, output_format="JPEG", caption=f"{movie_name[movie_index]} ({movie_year[movie_index]}) - Rating: {movie_rating[movie_index]}")
