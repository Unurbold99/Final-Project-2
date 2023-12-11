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

# Create input_data DataFrame with numerical features
input_data = pd.DataFrame({
    'age': [st.number_input("Age:")],
    'player_height': [st.number_input("Player Height:")],
    'player_weight': [st.number_input("Player Weight:")],
    'draft_number': [st.number_input("Draft Number:")],
    'years_in_nba': [st.number_input("Years in NBA:")],
})

# Add one-hot encoding columns using dict.fromkeys() for consistency
team_abbreviation_col = 'team_abbreviation_' + team_abbreviation
college_col = 'college_' + college

input_data[team_abbreviation_col] = 1
input_data[college_col] = 1

# Ensure that the input data has the same columns as the model was trained on
model_columns = loaded_model.get_booster().feature_names
missing_columns = set(model_columns) - set(input_data.columns)
input_data = input_data.reindex(columns=model_columns, fill_value=0)

# Make predictions
predictions = loaded_model.predict(input_data)

# Display predictions
st.write("Predictions:")
st.write("Games Played (gp):", predictions[0][0])
st.write("Points (pts):", predictions[0][1])
st.write("Rebounds (reb):", predictions[0][2])
st.write("Assists (ast):", predictions[0][3])
st.write("Net Rating (net_rating):", predictions[0][4])
