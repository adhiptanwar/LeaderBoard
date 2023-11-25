import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("Sadda Poker Leaderboard")

# Function to update ranks based on average per game
def update_ranks(df):
    df['Average Per Game'] = df['Winnings'] / (df['Games Played'].replace(0, 1))  # Handling division by zero
    df['Rank'] = df['Average Per Game'].rank(method='dense', ascending=False).astype(int)
    df = df.sort_values(by='Rank').reset_index(drop=True)
    return df

conn = st.connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="players", usecols=list(range(5)), ttl=5)
existing_data = existing_data.dropna(how="all")

st.dataframe(existing_data)

# Add input fields to update winnings or add a new player
st.header("Update Player Winnings or Add New Player")
option = st.radio("Select an option", ("Update Winnings", "Add New Player"))

if option == "Update Winnings":
    selected_player = st.radio(
    "Select a Player", existing_data["Player"].tolist())

    selected_player_row = existing_data[existing_data["Player"] == selected_player]

    # Display the selected player's current winnings
    st.write(f"Current Winnings for {selected_player}: {selected_player_row['Winnings'].values[0]}")

    # Input field to update winnings
    updated_winnings = st.number_input(f"Update Winnings for {selected_player}", value=0.0, step=0.1)

    if st.button("Update"):
        player_index = existing_data[existing_data["Player"] == selected_player].index
        if not player_index.empty:
            player_index = player_index[0]
            existing_data.at[player_index, "Winnings"] += updated_winnings
            existing_data.at[player_index, "Games Played"] += 1
            existing_data = update_ranks(existing_data)  # Update ranks based on averages
            conn.update(worksheet="players", data=existing_data)
            st.success(f"{selected_player}'s winnings updated!")

elif option == "Add New Player":
    new_player_name = st.text_input("Enter New Player's Name")

    if st.button("Add Player") and new_player_name.strip() != "":
        new_player_data = pd.DataFrame({
            "Player": [new_player_name],
            "Winnings": [0],  # Default value for Winnings
            "Games Played": [0],  # Default value for Games Played
            "Average Per Game": [0]  # Initialize Average Per Game as 0 for new player
        })
        existing_data = existing_data.append(new_player_data, ignore_index=True)
        existing_data = update_ranks(existing_data)  # Update ranks based on averages
        conn.update(worksheet="players", data=existing_data)
        st.success(f"New player {new_player_name} added!")

st.header("Update Leader Board")
if st.button("Update Board"):
    st.experimental_rerun()
    
