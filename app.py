from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

# Global variables to store the trained model and info
model_pipeline = None
model_info = None

def load_saved_model():
    """Load your pre-trained model from file"""
    global model_pipeline, model_info
    
    model_file = 'lol_model.pkl'
    info_file = 'model_info.pkl'
    
    # Check if model files exist
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Model file '{model_file}' not found. Please run 'python train_model.py' first to create the model.")
    
    # Load the trained model
    with open(model_file, 'rb') as f:
        model_pipeline = pickle.load(f)
    
    # Load model info if available
    if os.path.exists(info_file):
        with open(info_file, 'rb') as f:
            model_info = pickle.load(f)
        print(f"Model loaded successfully! Accuracy: {model_info['accuracy']:.2f}")
        print(f"Features: {model_info['feature_names']}")
    else:
        print("Model loaded successfully!")
    
    return model_pipeline

def predict_win_probability(team_kills, team_deaths, team_assists, 
                          enemy_kills, enemy_deaths, enemy_assists,
                          team_gold, enemy_gold, dragon_acquisition):
    """
    Predict win probability based on game statistics using your trained model
    dragon_acquisition: 'team', 'enemy', or 'none'
    """
    global model_pipeline
    
    if model_pipeline is None:
        raise ValueError("Model not loaded!")
    
    # Calculate derived features exactly as in your notebook
    team_kda = (team_kills + team_assists) / max(1, team_deaths)
    enemy_kda = (enemy_kills + enemy_assists) / max(1, enemy_deaths)
    gold_diff = team_gold - enemy_gold
    
    # Convert dragon acquisition to numeric (based on your data analysis)
    # From the CSV, dragon seems to be: 0=none, 1=team advantage, 2=more dragons
    if dragon_acquisition.lower() == 'team':
        dragon = 1
    elif dragon_acquisition.lower() == 'enemy':
        dragon = 0  # Enemy having dragons would be unfavorable for team
    else:  # none
        dragon = 0
    
    # Calculate gold per kill
    total_kills = team_kills + enemy_kills
    gold_per_kill = (team_gold + enemy_gold) / max(1, total_kills)
    
    # Create input dataframe with the exact features your model was trained on
    # Order: ['dragon', 'gold_diff', 'gold_per_kill', 'team_kda', 'enemy_kda']
    input_data = pd.DataFrame({
        'dragon': [dragon],
        'gold_diff': [gold_diff],
        'gold_per_kill': [gold_per_kill],
        'team_kda': [team_kda],
        'enemy_kda': [enemy_kda]
    })
    
    # Get prediction probability
    win_probability = model_pipeline.predict_proba(input_data)[0][1]
    
    return win_probability

@app.route('/')
def index():
    """Home page with the input form"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for predictions"""
    try:
        data = request.json
        
        # Extract data from request
        team_kills = int(data['team_kills'])
        team_deaths = int(data['team_deaths'])
        team_assists = int(data['team_assists'])
        enemy_kills = int(data['enemy_kills'])
        enemy_deaths = int(data['enemy_deaths'])
        enemy_assists = int(data['enemy_assists'])
        team_gold = int(data['team_gold'])
        enemy_gold = int(data['enemy_gold'])
        dragon_acquisition = data['dragon_acquisition']
        
        # Get prediction
        win_prob = predict_win_probability(
            team_kills, team_deaths, team_assists,
            enemy_kills, enemy_deaths, enemy_assists,
            team_gold, enemy_gold, dragon_acquisition
        )
        
        return jsonify({
            'success': True,
            'win_probability': round(win_prob * 100, 2),
            'message': f'Your team has a {round(win_prob * 100, 2)}% chance of winning!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    # Load your pre-trained model on startup
    try:
        load_saved_model()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run 'python train_model.py' first to create the model.")
        exit(1)
    
    app.run(debug=True, host='0.0.0.0', port=5000)