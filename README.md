# League of Legends Win Predictor

A machine learning-powered web application that predicts the probability of winning a League of Legends match based on current game statistics.

## 🚀 Live Demo

Deploy to Vercel with one click: [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/lol-win-predictor)

## 📋 Features

- **Real-time Predictions**: Get instant win probability based on current game stats
- **Interactive UI**: Beautiful, responsive web interface with League of Legends theme
- **Model Transparency**: See exactly what parameters the ML model uses
- **Serverless Deployment**: Optimized for Vercel's serverless platform
- **Colorblind Accessible**: Uses colorblind-friendly color schemes

## 🏗️ Project Structure

```
lol-win-predictor/
├── api/
│   └── app.py                 # Vercel serverless function
├── templates/                 # Original Flask templates (for reference)
│   └── index.html
├── index.html                 # Static HTML for Vercel
├── vercel.json               # Vercel configuration
├── requirements.txt          # Python dependencies
├── lol_model.pkl            # Trained ML model
├── model_info.pkl           # Model metadata
├── League_of_Legends_data.csv # Training data
├── Test_Model.ipynb         # Comprehensive model analysis
└── README.md                # This file
```

## 🤖 Machine Learning Model

The prediction model uses **Logistic Regression** trained on League of Legends match data with these key features:

- **Team KDA**: (Kills + Assists) / Deaths ratio for your team
- **Enemy KDA**: (Kills + Assists) / Deaths ratio for enemy team  
- **Gold Difference**: Your team's gold minus enemy team's gold
- **Gold per Kill**: Total gold divided by total kills (game efficiency)
- **Dragon Acquisition**: Whether your team, enemy team, or neither has dragon advantage

**Model Performance**: ~85% accuracy on test data

## 🚀 Deployment to Vercel

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub recommended)

### Method 1: Deploy from GitHub (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/lol-win-predictor.git
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the configuration

3. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy your app
   - You'll get a live URL like `https://lol-win-predictor.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd your-project-directory
   vercel
   ```

   Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - Project name: **lol-win-predictor**
   - Directory: **.//** (current directory)

### Method 3: Drag & Drop Deploy

1. Create a ZIP file of your entire project directory
2. Go to [vercel.com/new](https://vercel.com/new)
3. Drag and drop the ZIP file
4. Follow the deployment wizard

## 🔧 Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/",
      "dest": "/index.html"
    },
    {
      "src": "/api/(.*)",
      "dest": "api/app.py"
    }
  ],
  "functions": {
    "api/app.py": {
      "maxDuration": 30
    }
  }
}
```

### requirements.txt
```
Flask==2.3.3
pandas==2.0.3
scikit-learn==1.3.0
numpy==1.24.3
gunicorn==21.2.0
```

## 🧪 Local Development

### Option 1: Using the original Flask app
```bash
python app.py
```
Visit `http://localhost:5000`

### Option 2: Using Vercel CLI for local testing
```bash
vercel dev
```
Visit `http://localhost:3000`

## 📊 Model Analysis

The project includes a comprehensive Jupyter notebook (`Test_Model.ipynb`) with:

- Feature importance analysis
- Win probability heatmaps
- Dragon impact analysis
- Gold efficiency analysis
- Model confidence analysis
- Sensitivity analysis
- Decision boundary visualization

All visualizations use colorblind-friendly color schemes.

## 🔍 API Endpoints

### POST /api/predict

Predicts win probability based on game statistics.

**Request Body**:
```json
{
  "team_kills": 15,
  "team_deaths": 8,
  "team_assists": 22,
  "team_gold": 45000,
  "enemy_kills": 12,
  "enemy_deaths": 15,
  "enemy_assists": 18,
  "enemy_gold": 42000,
  "dragon_acquisition": "team"
}
```

**Response**:
```json
{
  "success": true,
  "win_probability": 73.2,
  "message": "Your team has a 73.2% chance of winning!"
}
```

## 🎯 Usage

1. Enter your team's current statistics (kills, deaths, assists, gold)
2. Enter the enemy team's statistics
3. Select who has dragon advantage
4. Click "Predict Win Probability"
5. View your win percentage and model parameters

## 🛠️ Technologies Used

- **Backend**: Python, Flask, scikit-learn, pandas, numpy
- **Frontend**: HTML, CSS, JavaScript
- **ML Model**: Logistic Regression
- **Deployment**: Vercel Serverless Functions
- **Data Analysis**: Jupyter Notebook, matplotlib, seaborn

## 📈 Model Training

The model was trained on League of Legends match data using:
- Feature engineering (KDA ratios, gold differences)
- Logistic regression for binary classification
- Cross-validation for model evaluation
- Feature importance analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This predictor is for educational and entertainment purposes. Actual game outcomes depend on many factors not captured in this model, including player skill, teamwork, and strategic decisions.

## 🔗 Links

- **Live Demo**: https://your-app.vercel.app
- **Repository**: https://github.com/yourusername/lol-win-predictor
- **Vercel Documentation**: https://vercel.com/docs

---

**Made with ❤️ for the League of Legends community**