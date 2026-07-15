import os
import zipfile
import subprocess
import pandas as pd
import json
from datetime import datetime

# ==========================================
# 1. DOWNLOAD DATA FROM KAGGLE
# ==========================================
DATASET_NAME = "davidcariboo/player-scores"
DATA_DIR = "./transfermarkt_data"

def download_and_extract_kaggle_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    print(f"Downloading dataset {DATASET_NAME} from Kaggle...")
    # Note: Requires Kaggle API token (~/.kaggle/kaggle.json)
    # subprocess.run(["kaggle", "datasets", "download", "-d", DATASET_NAME, "-p", DATA_DIR], check=True)
    
    zip_path = os.path.join(DATA_DIR, "player-scores.zip")
    print("Extracting files...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    
    print("Download and extraction complete.")

# ==========================================
# 2. DOMAIN MAPPING CONFIGURATION
# ==========================================
LEAGUE_TIERS = {
    'GB1': 'Tier 1', 'ES1': 'Tier 1', 'IT1': 'Tier 1', 'L1': 'Tier 1', # EPL, LaLiga, Serie A, Bundesliga
    'FR1': 'Tier 2', 'PO1': 'Tier 2', 'NL1': 'Tier 2',                 # Ligue 1, Primeira Liga, Eredivisie
    'MLS1': 'Tier 3', 'TR1': 'Tier 3', 'BE1': 'Tier 3',                # MLS, Super Lig, Pro League
}

def map_league_tier(comp_id):
    return LEAGUE_TIERS.get(comp_id, 'Tier 4')

def map_position(pos):
    pos = str(pos).lower()
    if 'attack' in pos or 'forward' in pos or 'winger' in pos:
        return 'FW'
    elif 'midfield' in pos:
        return 'MF'
    elif 'back' in pos or 'defend' in pos:
        return 'DF'
    elif 'goalkeeper' in pos:
        return 'GK'
    return 'Unknown'

# ==========================================
# 3. PROCESS AND CONVERT TO JSON
# ==========================================
def process_data_to_json():
    print("Loading CSV files into Pandas...")
    
    players_df = pd.read_csv(os.path.join(DATA_DIR, "players.csv"))
    transfers_df = pd.read_csv(os.path.join(DATA_DIR, "transfers.csv"))
    clubs_df = pd.read_csv(os.path.join(DATA_DIR, "clubs.csv"))
    valuations_df = pd.read_csv(os.path.join(DATA_DIR, "player_valuations.csv"))
    appearances_df = pd.read_csv(os.path.join(DATA_DIR, "appearances.csv"))

    print("Processing domain logic...")

    # Create mapping dictionaries for rapid lookups
    club_to_league = dict(zip(clubs_df['club_id'], clubs_df['domestic_competition_id']))
    club_names = dict(zip(clubs_df['club_id'], clubs_df['name']))

    # ==========================================
    # PHASE A: GENERATE CURRENT PLAYERS
    # ==========================================
    print("Generating current_players.json for Views 1 & 2...")
    
    # Aggregate raw performance stats for the player profiles
    stats_agg = appearances_df.groupby('player_id').agg({
        'minutes_played': 'sum',
        'goals': 'sum',
        'assists': 'sum'
    }).reset_index()
    stats_dict = stats_agg.set_index('player_id').to_dict('index')

    current_players = []
    
    for _, player in players_df.iterrows():
        player_id = player['player_id']
        current_club_id = player.get('current_club_id')
        
        # Skip players who are retired or unattached
        if pd.isna(current_club_id):
            continue
            
        league_id = club_to_league.get(current_club_id, 'Unknown')
        
        # Calculate Current Age
        dob = pd.to_datetime(player.get('date_of_birth', pd.NaT))
        age = None
        if pd.notna(dob):
            age = int((pd.Timestamp.now() - dob).days / 365.25)
            
        # Fetch stats, defaulting to 0 if no appearances are recorded
        p_stats = stats_dict.get(player_id, {"minutes_played": 0, "goals": 0, "assists": 0})
        
        current_players.append({
            "player_id": int(player_id),
            "player_name": player.get('name', 'Unknown'),
            "position": map_position(player.get('position', 'Unknown')),
            "age": age,
            "current_club": club_names.get(current_club_id, 'Unknown Club'),
            "current_league": str(league_id),
            "current_league_tier": map_league_tier(league_id),
            "current_market_value_eur": float(player.get('market_value_in_eur', 0) or 0),
            "image_url": player.get('image_url', ''),
            "metrics": {
                "minutes_played": int(p_stats['minutes_played']),
                "goals": int(p_stats['goals']),
                "assists": int(p_stats['assists'])
            }
        })
        
    with open("current_players.json", "w") as f:
        json.dump(current_players, f, indent=4)
        
    print(f"Successfully exported {len(current_players)} current players.")

    # ==========================================
    # PHASE B: GENERATE HISTORICAL TRANSITIONS
    # ==========================================
    print("Generating historical_transitions.json for View 3...")
    
    transfers_df['transfer_date'] = pd.to_datetime(transfers_df['transfer_date'], errors='coerce')
    recent_transfers = transfers_df[transfers_df['transfer_date'] >= '2019-01-01'].copy()

    processed_transfers = []
    players_df.set_index('player_id', inplace=True)

    for _, transfer in recent_transfers.iterrows():
        player_id = transfer['player_id']
        
        if player_id not in players_df.index:
            continue
            
        player_info = players_df.loc[player_id]
        from_club_id = transfer['from_club_id']
        to_club_id = transfer['to_club_id']
        
        from_league_id = club_to_league.get(from_club_id, 'Unknown')
        to_league_id = club_to_league.get(to_club_id, 'Unknown')
        
        if from_club_id == to_club_id or pd.isna(from_league_id) or pd.isna(to_league_id):
            continue

        # Extract market valuations surrounding the transition date
        player_vals = valuations_df[valuations_df['player_id'] == player_id].copy()
        if player_vals.empty:
            continue
            
        player_vals['date'] = pd.to_datetime(player_vals['date'])
        
        vals_before = player_vals[player_vals['date'] <= transfer['transfer_date']]
        if vals_before.empty:
            continue
        val_before = vals_before.sort_values(by='date', ascending=False).iloc[0]['market_value_in_eur']

        date_plus_6m = transfer['transfer_date'] + pd.DateOffset(months=6)
        date_plus_18m = transfer['transfer_date'] + pd.DateOffset(months=18)
        
        vals_after = player_vals[(player_vals['date'] >= date_plus_6m) & (player_vals['date'] <= date_plus_18m)]
        if vals_after.empty:
            continue
        val_after = vals_after.sort_values(by='date', ascending=True).iloc[0]['market_value_in_eur']

        # Calculate Age at the specific time of transfer
        dob = pd.to_datetime(player_info.get('date_of_birth', pd.NaT))
        age_at_transfer = None
        if pd.notna(dob):
            age_at_transfer = int((transfer['transfer_date'] - dob).days / 365.25)

        processed_transfers.append({
            "player_id": int(player_id),
            "player_name": player_info.get('name', 'Unknown'),
            "position": map_position(player_info.get('position', 'Unknown')),
            "age_at_transfer": age_at_transfer,
            "transfer_date": transfer['transfer_date'].strftime('%Y-%m-%d'),
            "origin": {
                "club_id": int(from_club_id),
                "club_name": club_names.get(from_club_id, 'Unknown Club'),
                "league_tier": map_league_tier(from_league_id)
            },
            "destination": {
                "club_id": int(to_club_id),
                "club_name": club_names.get(to_club_id, 'Unknown Club'),
                "league_tier": map_league_tier(to_league_id)
            },
            "financials": {
                "market_value_before_eur": float(val_before),
                "market_value_after_eur": float(val_after),
                "value_change_percentage": round(((val_after - val_before) / val_before) * 100, 2) if val_before > 0 else 0
            }
        })

    with open("historical_transitions.json", "w") as f:
        json.dump(processed_transfers, f, indent=4)
        
    print(f"Successfully exported {len(processed_transfers)} historical transitions.")
    print("Data processing pipeline complete.")

if __name__ == "__main__":
    download_and_extract_kaggle_data()
    process_data_to_json()