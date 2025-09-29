#!/usr/bin/env python3
"""
LoL Win Predictor - Python Model Service
Uses the trained scikit-learn model for predictions
"""

import pickle
import pandas as pd
import os
import sys
from typing import Dict, Any, Tuple

class LoLWinPredictor:
    """League of Legends Win Prediction Model"""
    
    def __init__(self, model_path: str = 'lol_model.pkl', info_path: str = 'model_info.pkl'):
        """
        Initialize the predictor with trained model
        
        Args:
            model_path: Path to the trained model file
            info_path: Path to the model info file
        """
        self.model = None
        self.model_info = None
        self.is_loaded = False
        
        # Try to load the model
        self.load_model(model_path, info_path)
    
    def load_model(self, model_path: str, info_path: str) -> bool:
        """
        Load the trained model and model info
        
        Args:
            model_path: Path to the model pickle file
            info_path: Path to the model info pickle file
            
        Returns:
            bool: True if model loaded successfully
        """
        try:
            # Try different possible paths
            possible_paths = [
                (model_path, info_path),
                (f'../{model_path}', f'../{info_path}'),
                (f'../../{model_path}', f'../../{info_path}'),
                (f'./{model_path}', f'./{info_path}')
            ]
            
            for model_file, info_file in possible_paths:
                if os.path.exists(model_file) and os.path.exists(info_file):
                    # Load the model
                    with open(model_file, 'rb') as f:
                        self.model = pickle.load(f)
                    
                    # Load model info
                    with open(info_file, 'rb') as f:
                        self.model_info = pickle.load(f)
                    
                    self.is_loaded = True
                    print(f"✅ Model loaded successfully from {model_file}")
                    print(f"📊 Model accuracy: {self.model_info['accuracy']:.3f}")
                    print(f"🔧 Features: {self.model_info['feature_names']}")
                    return True
            
            print("❌ Could not find model files in any expected location")
            return False
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def calculate_features(self, team_kills: int, team_deaths: int, team_assists: int,
                          enemy_kills: int, enemy_deaths: int, enemy_assists: int,
                          team_gold: int, enemy_gold: int, dragon_acquisition: str) -> Dict[str, float]:
        """
        Calculate features from game statistics
        
        Args:
            team_kills: Your team's kills
            team_deaths: Your team's deaths  
            team_assists: Your team's assists
            enemy_kills: Enemy team's kills
            enemy_deaths: Enemy team's deaths
            enemy_assists: Enemy team's assists
            team_gold: Your team's total gold
            enemy_gold: Enemy team's total gold
            dragon_acquisition: 'team', 'enemy', or 'none'
            
        Returns:
            Dict with calculated features
        """
        # Calculate KDA ratios
        team_kda = (team_kills + team_assists) / max(1, team_deaths)
        enemy_kda = (enemy_kills + enemy_assists) / max(1, enemy_deaths)
        
        # Calculate gold metrics
        gold_diff = team_gold - enemy_gold
        total_kills = team_kills + enemy_kills
        gold_per_kill = (team_gold + enemy_gold) / max(1, total_kills)
        
        # Convert dragon acquisition to numeric
        dragon = 1 if dragon_acquisition.lower() == 'team' else 0
        
        return {
            'dragon': dragon,
            'gold_diff': gold_diff,
            'gold_per_kill': gold_per_kill,
            'team_kda': team_kda,
            'enemy_kda': enemy_kda
        }
    
    def predict(self, team_kills: int, team_deaths: int, team_assists: int,
                enemy_kills: int, enemy_deaths: int, enemy_assists: int,
                team_gold: int, enemy_gold: int, dragon_acquisition: str) -> Dict[str, Any]:
        """
        Make a win prediction
        
        Args:
            Game statistics (same as calculate_features)
            
        Returns:
            Dict with prediction results
        """
        if not self.is_loaded:
            return {
                'success': False,
                'error': 'Model not loaded. Please check model files.'
            }
        
        try:
            # Calculate features
            features = self.calculate_features(
                team_kills, team_deaths, team_assists,
                enemy_kills, enemy_deaths, enemy_assists,
                team_gold, enemy_gold, dragon_acquisition
            )
            
            # Create DataFrame with correct feature order
            input_data = pd.DataFrame([features])
            
            # Make prediction
            win_probability = float(self.model.predict_proba(input_data)[0][1])
            prediction = int(self.model.predict(input_data)[0])
            
            return {
                'success': True,
                'win_probability': round(win_probability * 100, 2),
                'raw_probability': win_probability,
                'prediction': prediction,
                'prediction_label': 'WIN' if prediction == 1 else 'LOSE',
                'calculated_stats': {
                    'team_kda': round(features['team_kda'], 2),
                    'enemy_kda': round(features['enemy_kda'], 2),
                    'gold_difference': features['gold_diff'],
                    'gold_per_kill': round(features['gold_per_kill'], 0),
                    'dragon_advantage': dragon_acquisition
                },
                'model_info': {
                    'accuracy': round(self.model_info['accuracy'], 3),
                    'algorithm': 'Logistic Regression with StandardScaler',
                    'features': self.model_info['feature_names']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Prediction error: {str(e)}'
            }
    
    def test_prediction(self, team_kills: int, team_deaths: int, team_assists: int,
                       enemy_kills: int, enemy_deaths: int, enemy_assists: int,
                       team_gold: int, enemy_gold: int, dragon_acquisition: str = 'none') -> None:
        """
        Test prediction with detailed output (same as notebook function)
        """
        result = self.predict(
            team_kills, team_deaths, team_assists,
            enemy_kills, enemy_deaths, enemy_assists,
            team_gold, enemy_gold, dragon_acquisition
        )
        
        if not result['success']:
            print(f"❌ Error: {result['error']}")
            return
        
        # Display results like in the notebook
        print("=" * 50)
        print("INPUT STATISTICS:")
        print(f"Your Team:   {team_kills}K/{team_deaths}D/{team_assists}A | {team_gold:,} gold")
        print(f"Enemy Team:  {enemy_kills}K/{enemy_deaths}D/{enemy_assists}A | {enemy_gold:,} gold")
        print(f"Dragons:     {dragon_acquisition.title()}")
        
        print("\nCALCULATED FEATURES:")
        stats = result['calculated_stats']
        print(f"Team KDA:        {stats['team_kda']}")
        print(f"Enemy KDA:       {stats['enemy_kda']}")
        print(f"Gold Difference: {stats['gold_difference']:+,}")
        print(f"Gold per Kill:   {stats['gold_per_kill']:.0f}")
        print(f"Dragon Value:    {1 if dragon_acquisition.lower() == 'team' else 0}")
        
        print("\nPREDICTION:")
        print(f"Win Probability: {result['win_probability']}%")
        print(f"Result:          {result['prediction_label']}")
        print(f"Model Accuracy:  {result['model_info']['accuracy']}")
        print("=" * 50)


def main():
    """Command line interface"""
    if len(sys.argv) == 1:
        # Interactive mode
        print("🎮 LoL Win Predictor - Interactive Mode")
        print("=" * 40)
        
        predictor = LoLWinPredictor()
        if not predictor.is_loaded:
            print("Failed to load model. Exiting.")
            sys.exit(1)
        
        print("\nEnter game statistics:")
        try:
            team_kills = int(input("Your team kills: "))
            team_deaths = int(input("Your team deaths: "))
            team_assists = int(input("Your team assists: "))
            enemy_kills = int(input("Enemy team kills: "))
            enemy_deaths = int(input("Enemy team deaths: "))
            enemy_assists = int(input("Enemy team assists: "))
            team_gold = int(input("Your team gold: "))
            enemy_gold = int(input("Enemy team gold: "))
            dragon = input("Dragon advantage (team/enemy/none): ").strip().lower()
            
            predictor.test_prediction(
                team_kills, team_deaths, team_assists,
                enemy_kills, enemy_deaths, enemy_assists,
                team_gold, enemy_gold, dragon
            )
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
        except Exception as e:
            print(f"Error: {e}")
    
    elif len(sys.argv) == 10:
        # Command line mode (for API calls)
        try:
            args = sys.argv[1:]
            team_kills, team_deaths, team_assists = map(int, args[:3])
            enemy_kills, enemy_deaths, enemy_assists = map(int, args[3:6])
            team_gold, enemy_gold = map(int, args[6:8])
            dragon_acquisition = args[8]
            
            predictor = LoLWinPredictor()
            result = predictor.predict(
                team_kills, team_deaths, team_assists,
                enemy_kills, enemy_deaths, enemy_assists,
                team_gold, enemy_gold, dragon_acquisition
            )
            
            # Output JSON for API
            import json
            print(json.dumps(result))
            
        except Exception as e:
            import json
            error_result = {'success': False, 'error': str(e)}
            print(json.dumps(error_result))
            sys.exit(1)
    
    else:
        print("Usage:")
        print("  python model.py  # Interactive mode")
        print("  python model.py <team_kills> <team_deaths> <team_assists> <enemy_kills> <enemy_deaths> <enemy_assists> <team_gold> <enemy_gold> <dragon_acquisition>")


if __name__ == '__main__':
    main()