import streamlit as st
import pandas as pd
import joblib

# Load the saved Random Forest model
loaded_model = joblib.load('nba_random_forest_model.joblib')

# Load your NBA player dataset (replace 'your_dataset.csv' with your actual file)
df = pd.read_csv('your_dataset.csv')

# Streamlit app
st.title("NBA Player Prediction App")

# Get input features from the user
team_abbreviation_options = df['team_abbreviation'].unique()
team_abbreviation = st.selectbox("Team Abbreviation:", team_abbreviation_options)

age = st.number_input("Age:")
player_height = st.number_input("Player Height:")
player_weight = st.number_input("Player Weight:")

college_options = df['college'].unique()
college = st.selectbox("College:", college_options)

draft_number = st.number_input("Draft Number:")
years_in_nba = st.number_input("Years in NBA:")

# Convert categorical features to one-hot encoding
team_abbreviation_dummy = pd.get_dummies(pd.Series([team_abbreviation]), prefix='team_abbreviation')
college_dummy = pd.get_dummies(pd.Series([college]), prefix='college')

# Concatenate numerical and one-hot encoded features
input_data = pd.DataFrame({
    'age': [age],
    'player_height': [player_height],
    'player_weight': [player_weight],
    'draft_number': [draft_number],
    'years_in_nba': [years_in_nba],
}).join(team_abbreviation_dummy).join(college_dummy)

# Make predictions
predictions = loaded_model.predict(input_data)

# Display predictions
st.write("Predictions:")
st.write("Games Played (gp):", predictions[0][0])
st.write("Points (pts):", predictions[0][1])
st.write("Rebounds (reb):", predictions[0][2])
st.write("Assists (ast):", predictions[0][3])
st.write("Net Rating (net_rating):", predictions[0][4])
