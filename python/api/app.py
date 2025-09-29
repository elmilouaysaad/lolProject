from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os

# Create Flask app
app = Flask(__name__)

# Global variables to store the trained model and info
model_pipeline = None
model_info = None

def load_saved_model():
    """Load your pre-trained model from file"""
    global model_pipeline, model_info
    
    # Try multiple paths for Vercel deployment
    possible_paths = [
        # Current directory
        ('lol_model.pkl', 'model_info.pkl'),
        # Parent directory
        ('../lol_model.pkl', '../model_info.pkl'),
        # Root directory
        (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lol_model.pkl'),
         os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model_info.pkl')),
        # Absolute paths for Vercel
        ('/var/task/lol_model.pkl', '/var/task/model_info.pkl')
    ]
    
    model_file = None
    info_file = None
    
    for model_path, info_path in possible_paths:
        if os.path.exists(model_path):
            model_file = model_path
            info_file = info_path
            break
    
    if model_file is None:
        # List current directory contents for debugging
        current_dir = os.getcwd()
        files = os.listdir(current_dir)
        raise FileNotFoundError(f"Model file not found. Current directory: {current_dir}, Files: {files}")
    
    # Load the trained model
    with open(model_file, 'rb') as f:
        model_pipeline = pickle.load(f)
    
    # Load model info if available
    if os.path.exists(info_file):
        with open(info_file, 'rb') as f:
            model_info = pickle.load(f)
    
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
        load_saved_model()
    
    # Calculate derived features exactly as in your notebook
    team_kda = (team_kills + team_assists) / max(1, team_deaths)
    enemy_kda = (enemy_kills + enemy_assists) / max(1, enemy_deaths)
    gold_diff = team_gold - enemy_gold
    
    # Convert dragon acquisition to numeric
    if dragon_acquisition.lower() == 'team':
        dragon = 1
    elif dragon_acquisition.lower() == 'enemy':
        dragon = 0
    else:  # none
        dragon = 0
    
    # Calculate gold per kill
    total_kills = team_kills + enemy_kills
    gold_per_kill = (team_gold + enemy_gold) / max(1, total_kills)
    
    # Create input dataframe with the exact features your model was trained on
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

@app.route('/', methods=['GET'])
@app.route('/api', methods=['GET'])
def root():
    """Root endpoint for API status"""
    return jsonify({
        'status': 'LoL Win Predictor API is running',
        'endpoints': ['/api/predict', '/api/health']
    })

@app.route('/predict', methods=['POST'])
@app.route('/api/predict', methods=['POST'])  # Support both routes
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

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        import os
        current_dir = os.getcwd()
        files = os.listdir(current_dir)
        
        # Try to load the model to verify everything works
        if model_pipeline is None:
            load_saved_model()
        
        return jsonify({
            'status': 'healthy',
            'model_loaded': model_pipeline is not None,
            'current_directory': current_dir,
            'files_in_directory': files[:10],  # Show first 10 files
            'python_path': os.path.abspath(__file__)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'current_directory': os.getcwd(),
            'files_in_directory': os.listdir(os.getcwd())[:10]
        }), 500

# For local testing
if __name__ == '__main__':
    app.run(debug=True)

# Vercel entry point - expose the app
def handler(request, response):
    return app(request, response)