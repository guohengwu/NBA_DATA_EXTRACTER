import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, shotchartdetail
from nba_api.stats.static import teams, players

# Set up the Streamlit app title
st.title("NBA Raw Game Data Extractor")

# Sidebar for user input
st.sidebar.header("Select Criteria for Data Extraction")

# Data type selection
data_type = st.sidebar.selectbox("Select Data Type", ["Game Data", "Shot Chart Data"])

# Common data (team selection)
all_teams = teams.get_teams()
team_names = [team['full_name'] for team in all_teams]

# Select Team for Data Extraction
team_name = st.sidebar.selectbox("Select a Team", team_names)

# Date range for filtering data (Game Data only)
if data_type == "Game Data":
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

# Player selection (Shot Chart Data only)
if data_type == "Shot Chart Data":
    players_data = players.get_players()
    player_name = st.sidebar.text_input("Enter Player Name (e.g., LeBron James)", "LeBron James")

    # Sidebar inputs for season and game type (Shot Chart Data only)
    if player_name:
        season = st.sidebar.selectbox("Select Season", ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22"])
        game_type = st.sidebar.selectbox("Select Game Type", ["Playoffs", "Regular Season"])

# Button to execute the data extraction
if st.sidebar.button("Extract Data"):
    if data_type == "Game Data":
        # Find the selected team ID
        selected_team = next((team for team in all_teams if team['full_name'] == team_name), None)
        if selected_team:
            team_id = selected_team['id']
            
            # Query games played by the selected team
            gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
            games = gamefinder.get_data_frames()[0]

            # Convert GAME_DATE to datetime
            games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])
            
            # Filter games by selected date range
            games_filtered = games[(games['GAME_DATE'] >= pd.to_datetime(start_date)) & (games['GAME_DATE'] <= pd.to_datetime(end_date))]
            
            # Display the extracted data
            st.write("### Extracted Game Data for", team_name)
            st.dataframe(games_filtered)

            # Add download button
            
        else:
            st.write("Team not found. Please try again.")

    elif data_type == "Shot Chart Data":
        # Find player ID by name
        player = next((player for player in players_data if player['full_name'].lower() == player_name.lower()), None)
        if player:
            player_id = player['id']

            # Ensure season and game type are selected before proceeding
            if 'season' in locals() and 'game_type' in locals():
                # Get shotchart details
                response = shotchartdetail.ShotChartDetail(
                    team_id=0,  # 0 to ignore team filter
                    player_id=player_id,
                    context_measure_simple='FGA',  # Field Goal Attempts
                    season_nullable=season,
                    season_type_all_star=game_type
                )

                # Get data as DataFrame
                shot_data = response.get_data_frames()[0]

                if not shot_data.empty:
                    # Display the extracted data
                    st.write(f"### Shot Chart Data for {player_name} ({season} {game_type})")
                    st.dataframe(shot_data)

                    
                else:
                    st.write(f"No shot chart data found for {player_name} in the selected {season} {game_type}.")
            else:
                st.write("Please select both a season and game type.")
        else:
            st.write("Player not found. Please check the name.")

# Footer for additional information or instructions
st.sidebar.write("Note: Use the official NBA API endpoints for real-time data. This app is for educational purposes.")
