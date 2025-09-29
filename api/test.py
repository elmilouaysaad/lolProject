from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Simple rule-based prediction as fallback
def simple_prediction(team_kills, team_deaths, team_assists, 
                     enemy_kills, enemy_deaths, enemy_assists,
                     team_gold, enemy_gold, dragon_acquisition):
    """
    Simple rule-based prediction when ML model isn't available
    """
    # Calculate basic stats
    team_kda = (team_kills + team_assists) / max(1, team_deaths)
    enemy_kda = (enemy_kills + enemy_assists) / max(1, enemy_deaths)
    gold_diff = team_gold - enemy_gold
    
    # Simple scoring system
    score = 0
    
    # KDA advantage (40% weight)
    if team_kda > enemy_kda:
        score += 0.4 * min(0.8, (team_kda - enemy_kda) / 3.0)
    else:
        score -= 0.4 * min(0.8, (enemy_kda - team_kda) / 3.0)
    
    # Gold advantage (35% weight)
    if gold_diff > 0:
        score += 0.35 * min(0.8, gold_diff / 15000)
    else:
        score -= 0.35 * min(0.8, abs(gold_diff) / 15000)
    
    # Dragon advantage (25% weight)
    if dragon_acquisition.lower() == 'team':
        score += 0.25
    elif dragon_acquisition.lower() == 'enemy':
        score -= 0.25
    
    # Convert to probability (50% base + score adjustment)
    win_probability = 0.5 + score
    win_probability = max(0.05, min(0.95, win_probability))  # Clamp between 5% and 95%
    
    return win_probability

@app.route('/')
def root():
    return jsonify({
        'status': 'LoL Win Predictor API is running',
        'mode': 'Lightweight Rule-Based Prediction',
        'endpoints': ['/predict', '/health', '/test']
    })

@app.route('/test')
def test():
    return jsonify({
        'test': 'API is working', 
        'route': '/test',
        'domain': 'lol-project-gamma.vercel.app'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint using simple rules
    """
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
        
        # Get prediction using simple rules
        win_prob = simple_prediction(
            team_kills, team_deaths, team_assists,
            enemy_kills, enemy_deaths, enemy_assists,
            team_gold, enemy_gold, dragon_acquisition
        )
        
        return jsonify({
            'success': True,
            'win_probability': round(win_prob * 100, 2),
            'message': f'Your team has a {round(win_prob * 100, 2)}% chance of winning!',
            'note': 'Prediction based on rule-based algorithm (lightweight version)'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/health')
def health():
    try:
        current_dir = os.getcwd()
        files = os.listdir(current_dir)[:10]
        
        return jsonify({
            'status': 'healthy',
            'mode': 'lightweight',
            'current_directory': current_dir,
            'files_in_directory': files,
            'note': 'Running without ML dependencies'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)