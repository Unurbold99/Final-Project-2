import streamlit as st
import pandas as pd
import joblib

# Load the saved Random Forest model
loaded_model = joblib.load('nba_random_forest_model.joblib')

# Load your NBA player dataset (replace 'your_dataset.csv' with your actual file)
df = pd.read_csv('data/all_seasons.csv')

# Streamlit app
st.title("NBA Player Prediction App")

# Get unique values for team_abbreviation and college
team_abbreviation_options = df['team_abbreviation'].unique()
college_options = df['college'].unique()

# User selects team and college from dropdowns
team_abbreviation = st.selectbox("Team Abbreviation:", team_abbreviation_options)
college = st.selectbox("College:", college_options)

# Convert categorical features to one-hot encoding
all_team_dummies = pd.get_dummies(df['team_abbreviation'], prefix='team_abbreviation')
all_college_dummies = pd.get_dummies(df['college'], prefix='college')

# Create input_data DataFrame with numerical features and one-hot encoding
input_data = pd.DataFrame({
    'age': st.number_input("Age:"),
    'player_height': st.number_input("Player Height:"),
    'player_weight': st.number_input("Player Weight:"),
    'draft_number': st.number_input("Draft Number:"),
    'years_in_nba': st.number_input("Years in NBA:"),
})

# Add one-hot encoding columns using dict.fromkeys() for consistency
input_data = pd.concat([input_data, pd.get_dummies(dict.fromkeys([team_abbreviation], 'team_abbreviation'), prefix='team_abbreviation')],
                       axis=1)

input_data = pd.concat([input_data, pd.get_dummies(dict.fromkeys([college], 'college'), prefix='college')],
                       axis=1)

# Set the value for the selected team and college to 1
input_data['team_abbreviation_' + team_abbreviation] = 1
input_data['college_' + college] = 1

# Make predictions
predictions = loaded_model.predict(input_data)

# Display predictions
st.write("Predictions:")
st.write("Games Played (gp):", predictions[0][0])
st.write("Points (pts):", predictions[0][1])
st.write("Rebounds (reb):", predictions[0][2])
st.write("Assists (ast):", predictions[0][3])
st.write("Net Rating (net_rating):", predictions[0][4])
