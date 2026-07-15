# Soccer Solver Data Processing Scripts

This directory contains utility scripts for processing data used by the Soccer Solver application.

## Transfermarkt Dataset Preprocessing

This script transforms the Transfermarkt dataset from Kaggle into a consumable JSON format (`transfermarkt_data.json`) for the application. This is typically a one-time process.

### Prerequisites

- Python 3

### Instructions

1. **Download Dataset:** Download the dataset zip file from Kaggle: 
   [Transfermarkt Dataset](https://www.kaggle.com/datasets/davidcariboo/player-scores?resource=download)

2. **Prepare File:** Rename the downloaded zip file to `player-scores.zip` and place it in the `scripts/transfermarkt_data/` directory.

3. **Run Script:** Execute the preprocessing script:
   ```bash
   pip3 install -r requirements.txt
   python3 transfermarkt_data_preprocessing.py
   ```
   
   This will generate a `current_players.json` and `historical_transactions.json` files in the `scripts/` directory.
