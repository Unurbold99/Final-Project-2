import streamlit as st
import pandas as pd
import joblib

# Load the saved Random Forest model
loaded_model = joblib.load('nba_random_forest_model.joblib')

# Load your NBA player dataset (replace 'your_dataset.csv' with your actual file)
df = pd.read_csv('data/all_seasons.csv')

# Select the top 20 colleges and label the rest as 'Other'
top_colleges = df['college'].value_counts().nlargest(20).index
df['college'] = df['college'].apply(lambda x: x if x in top_colleges else 'Other')

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
    'age': [int(st.number_input("Age:", step=1))],
    'player_height': [int(st.number_input("Player Height (cm):", step=1))],
    'player_weight': [int(st.number_input("Player Weight (kg):", step=1))],
    'draft_number': [int(st.number_input("Draft Number:", step=1))],
    'years_in_nba': [int(st.number_input("Years in NBA:", step=1))],
})


# Add one-hot encoding columns using dict.fromkeys() for consistency
team_abbreviation_col = 'team_abbreviation_' + team_abbreviation
college_col = 'college_' + college

input_data[team_abbreviation_col] = 1
input_data[college_col] = 1

# Ensure that the input data has the same columns as the model was trained on
model_columns = loaded_model.feature_names_in_
missing_columns = set(model_columns) - set(input_data.columns)
input_data = input_data.reindex(columns=model_columns, fill_value=0)

# Make predictions
predictions = loaded_model.predict(input_data)

# Display predictions
st.markdown("<h1 style='text-align: center; color: #ff6347;'>Predictions</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 24px;'>Games Played (gp): <strong>{:.1f}</strong></p>".format(predictions[0][0]), unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 24px;'>Points (pts): <strong>{:.1f}</strong></p>".format(predictions[0][1]), unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 24px;'>Rebounds (reb): <strong>{:.1f}</strong></p>".format(predictions[0][2]), unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 24px;'>Assists (ast): <strong>{:.1f}</strong></p>".format(predictions[0][3]), unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 24px;'>Net Rating (net_rating): <strong>{:.1f}</strong></p>".format(predictions[0][4]), unsafe_allow_html=True)
