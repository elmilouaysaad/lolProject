#!/usr/bin/env python3
"""
Deployment verification script for LoL Win Predictor
"""

import os
import json

def check_files():
    """Check if all required files exist"""
    required_files = [
        'index.html',
        'vercel.json',
        'requirements.txt',
        'lol_model.pkl',
        'model_info.pkl',
        'api/app.py',
        'api/index.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_vercel_config():
    """Check vercel.json configuration"""
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check if builds section is correct
        builds = config.get('builds', [])
        if not builds:
            print("❌ No builds configuration found")
            return False
        
        if builds[0].get('src') != 'api/index.py':
            print("❌ Incorrect build source")
            return False
        
        print("✅ Vercel configuration looks good")
        return True
    except Exception as e:
        print(f"❌ Error checking vercel.json: {e}")
        return False

def check_model_files():
    """Check if model files can be loaded"""
    try:
        import pickle
        
        # Check model file
        with open('lol_model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        # Check model info file
        with open('model_info.pkl', 'rb') as f:
            model_info = pickle.load(f)
        
        print("✅ Model files can be loaded successfully")
        print(f"   - Model type: {type(model)}")
        print(f"   - Features: {model_info.get('feature_names', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading model files: {e}")
        return False

def main():
    """Main deployment check"""
    print("🚀 LoL Win Predictor Deployment Check")
    print("=" * 40)
    
    checks = [
        check_files(),
        check_vercel_config(),
        check_model_files()
    ]
    
    if all(checks):
        print("\n🎉 All checks passed! Ready to deploy to Vercel")
        print("\nDeployment commands:")
        print("1. git add .")
        print("2. git commit -m 'Deploy to Vercel'")
        print("3. git push origin main")
        print("4. Or use: vercel --prod")
    else:
        print("\n❌ Some checks failed. Please fix the issues before deploying.")

if __name__ == "__main__":
    main()