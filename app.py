import streamlit as st
import pandas as pd
import plotly.express as px


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="MovieLens Dashboard",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------
# Load the data
# -----------------------------
df = pd.read_csv("movie_ratings.csv")

# -----------------------------
# Dashboard title
# -----------------------------
st.title("🎬 MovieLens Dashboard")

st.write(
    "Explore movie ratings, genres, release years, and highly rated movies "
    "using the MovieLens dataset."
)

# -------------------------------------------
# Basic dataset information (general summary)
# -------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Ratings", f"{len(df):,}")

with col2:
    st.metric("Unique Movies", f"{df['movie_id'].nunique():,}")

with col3:
    st.metric("Average Rating", f"{df['rating'].mean():.2f}") #display as 2 decimal places

# -----------------------------
# Q1: Genre Breakdown
# -----------------------------
st.header("1. Genre Breakdown")

#Explains the chart's purpose to its corresponding question 
st.write(
    "A break down of the movies' genre distribution.\n\n "
    "Because movies can have multiple genres, each movie's genre list "
    "is split into individual genres before counting. A movie is counted once in each genre it belongs to. "
)


# Split the genres and create one row for each genre
genre_counts = (
    df.assign(genre=df["genres"].str.split("|"))
      .explode("genre")
      .groupby("genre")["movie_id"]
      .nunique() #how many unique movies belong to each genre
      .sort_values(ascending=True)
)


# Create horizontal bar chart and store it in fig
fig = px.bar(
    genre_counts,
    x=genre_counts.values,
    y=genre_counts.index,
    orientation="h",
    labels={
        "x": "Number of Movies",
        "y": "Genre"
    }
)

#Take the created chart and display it on the Streamlit webpage
st.plotly_chart(fig, width = "stretch")


# -----------------------------
# Q2: Genre Satisfaction
# -----------------------------
st.header("2. Genre Satisfaction")

st.write(
    "Average rating for each genre. Movies with multiple genres "
    "contribute their ratings to each applicable genre."
)

#Find the average rating for each genre (split the genres)
genre_ratings = (
    df.assign(genre=df["genres"].str.split("|"))
      .explode("genre")
      .groupby("genre")["rating"]
      .mean()
      .sort_values(ascending=False)
)

#Create horizontal bar chart and store it in fig
fig = px.bar(
    genre_ratings,
    x=genre_ratings.values,
    y=genre_ratings.index,
    orientation="h",
    color=genre_ratings.index,
    color_discrete_sequence=px.colors.qualitative.Pastel,
    labels={
        "x": "Average Rating",
        "y": "Genre"
    }
)

#When hover over bar chart, average rating is displayed to 2 decimal places
fig.update_traces(
    hovertemplate="Genre: %{y}<br>Average Rating: %{x:.2f}<extra></extra>"
)

#Modifies the appearance of the created Plotly chart
fig.update_layout(
    showlegend=False,  #don't show the chart legend
    yaxis=dict( 
    categoryorder="array", #have the genres displayed from highest-lowest avg rating
    categoryarray=genre_ratings.index[::-1] #reverses the order of the index
    )
)

#Take the created chart and display it on the Streamlit webpage
st.plotly_chart(fig, width = "stretch")


# -----------------------------
# Q3: Ratings Over Time
# -----------------------------
st.header("3. Ratings Over Time")

st.write(
    "Average movie rating by release year."
)

#Find the mix and max year of the dataset (the range of years the movies were from)
min_year = int(df["year"].min())
max_year = int(df["year"].max())

#Create interactive widget - slider to specify over what range of years want to view chart
year_range = st.slider(
    "Movie release year range:",
    min_value=min_year, #lowest year the slider can select
    max_value=max_year, #highest year the slider can select
    value=(min_year, max_year) #can choose from min-max year
)

#Remove movies that don't have a year (rows with missing NaN values)
filtered_df = df.dropna(subset=["year"])

#Keep the selected year range - within the min-max year range
filtered_df = filtered_df[
    filtered_df["year"].between(year_range[0], year_range[1])
]

#Calculate the average rating for each year
yearly_ratings = (
    filtered_df.groupby("year")["rating"]
    .mean()
    .sort_index() #sorts the years in chronological order
)

#Create line graph and store it in fig
fig = px.line(
    yearly_ratings,
    x=yearly_ratings.index,
    y=yearly_ratings.values,
    markers=True,
    labels={
        "x": "Movie Release Year",
        "y": "Average Rating"
    }
)

#When hover over bar chart, average rating is displayed to 2 decimal places
fig.update_traces(
    hovertemplate="Year: %{x}<br>Average Rating: %{y:.2f}<extra></extra>"
)

#Make the chart's y-axis range from 0-5, so the vertical scale doesn't change when move slider
fig.update_layout(
    yaxis=dict(range=[0, 5])
)

#Take the created chart and display it on the Streamlit webpage
st.plotly_chart(fig, width = "stretch")

# -----------------------------
# Q4: Best Movies With a Rating Floor
# -----------------------------
st.header("4. Best Movies With a Rating Floor")

st.write(
    "Top 5 rated movies after requiring a minimum number of ratings."
)

#Create the summary info needed before applying the floor
#Get the avg rating and the num of ratings (for each movie)
movie_stats = (
    df.groupby(["movie_id", "title"])
      .agg(
          average_rating=("rating", "mean"),
          rating_count=("rating", "count")
      )
      .reset_index()
)

#Add interactive widget - user selects the minimum number of ratings - the chart is different depending on which one chosen
rating_floor = st.selectbox(
    "Minimum number of ratings:",
    [50, 150]
)

#Get the top 5 movies from movies that have at least 50 or 150 ratings
top_movies = (
    movie_stats[movie_stats["rating_count"] >= rating_floor]
    .sort_values("average_rating", ascending=False) #sort the movies from highest avg rating to lowest
    .head(5)
)

#Create horizontal bar chart and store it in fig
fig = px.bar(
    top_movies,
    x="average_rating",
    y="title",
    orientation="h",
    color="title",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    labels={
        "average_rating": "Average Rating",
        "title": "Movie"
    }
)

#When hover over bar chart, average rating is displayed to 2 decimal places
fig.update_traces(
    hovertemplate="Movie: %{y}<br>Average Rating: %{x:.2f}<extra></extra>"
)

#Don't show the legend for the chart
fig.update_layout(showlegend=False)

#Take the created chart and display it on the Streamlit webpage
st.plotly_chart(fig, width = "stretch")