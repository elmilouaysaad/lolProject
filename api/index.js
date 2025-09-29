// LoL Win Predictor API - JavaScript Version with ML Model
const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Trained Model Parameters (extracted from Python scikit-learn model)
const MODEL_COEFFICIENTS = {
  intercept: 0.16557694182444183,
  coefficients: {
    dragon: -0.06754431637790291,
    gold_diff: 1.107003659509875,
    gold_per_kill: -0.04172765965075479,
    team_kda: 0.18168310391014147,
    enemy_kda: 0.1254660638024227,
  }
};

const SCALER_PARAMS = {
  mean: {
    dragon: 0.743439226519337,
    gold_diff: 91.50207182320442,
    gold_per_kill: 3273.1575801210556,
    team_kda: 1.5382003167182776,
    enemy_kda: 1.486699221816108,
  },
  scale: {
    dragon: 0.8319366312774551,
    gold_diff: 2008.1471700613831,
    gold_per_kill: 2309.458855246555,
    team_kda: 2.4424573288528224,
    enemy_kda: 2.3236194700520625,
  }
};

// ML Model Implementation in JavaScript
function mlPrediction(teamKills, teamDeaths, teamAssists, 
                     enemyKills, enemyDeaths, enemyAssists,
                     teamGold, enemyGold, dragonAcquisition) {
    
    // Calculate features exactly like the Python model
    const teamKda = (teamKills + teamAssists) / Math.max(1, teamDeaths);
    const enemyKda = (enemyKills + enemyAssists) / Math.max(1, enemyDeaths);
    const goldDiff = teamGold - enemyGold;
    const totalKills = teamKills + enemyKills;
    const goldPerKill = (teamGold + enemyGold) / Math.max(1, totalKills);
    const dragon = dragonAcquisition.toLowerCase() === 'team' ? 1 : 0;

    // Create features array
    const features = {
        dragon: dragon,
        gold_diff: goldDiff,
        gold_per_kill: goldPerKill,
        team_kda: teamKda,
        enemy_kda: enemyKda
    };

    // Apply StandardScaler normalization (same as Python)
    const scaledFeatures = {};
    for (const [feature, value] of Object.entries(features)) {
        scaledFeatures[feature] = (value - SCALER_PARAMS.mean[feature]) / SCALER_PARAMS.scale[feature];
    }

    // Calculate logistic regression prediction
    let logits = MODEL_COEFFICIENTS.intercept;
    for (const [feature, scaledValue] of Object.entries(scaledFeatures)) {
        logits += scaledValue * MODEL_COEFFICIENTS.coefficients[feature];
    }

    // Apply sigmoid function to get probability
    const winProbability = 1 / (1 + Math.exp(-logits));

    return {
        win_probability: winProbability,
        features: features,
        scaled_features: scaledFeatures,
        logits: logits
    };
}

// Routes
app.get('/', (req, res) => {
    res.json({
        status: 'LoL Win Predictor API is running',
        mode: 'Trained ML Model (Pure JavaScript)',
        endpoints: ['/api/predict', '/api/health', '/api/test'],
        version: '4.0.0',
        model_info: {
            accuracy: 0.701,
            algorithm: 'Logistic Regression with Standard Scaler',
            features: ['dragon', 'gold_diff', 'gold_per_kill', 'team_kda', 'enemy_kda']
        }
    });
});

app.get('/api', (req, res) => {
    res.json({
        status: 'LoL Win Predictor API is running',
        mode: 'Trained ML Model (Pure JavaScript)',
        endpoints: ['/api/predict', '/api/health', '/api/test'],
        version: '4.0.0',
        model_info: {
            accuracy: 0.701,
            algorithm: 'Logistic Regression with Standard Scaler',
            features: ['dragon', 'gold_diff', 'gold_per_kill', 'team_kda', 'enemy_kda']
        }
    });
});

app.get('/api/test', (req, res) => {
    res.json({
        test: 'JavaScript API is working',
        route: '/api/test',
        domain: 'lol-project-gamma.vercel.app',
        runtime: 'Pure JavaScript ML Model',
        timestamp: new Date().toISOString()
    });
});

app.post('/api/predict', (req, res) => {
    try {
        const {
            team_kills,
            team_deaths,
            team_assists,
            enemy_kills,
            enemy_deaths,
            enemy_assists,
            team_gold,
            enemy_gold,
            dragon_acquisition
        } = req.body;

        // Validate input
        if ([team_kills, team_deaths, team_assists, enemy_kills, enemy_deaths, enemy_assists, team_gold, enemy_gold].some(val => val === undefined || val === null)) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields'
            });
        }

        // Get prediction using trained ML model
        const prediction = mlPrediction(
            parseInt(team_kills),
            parseInt(team_deaths),
            parseInt(team_assists),
            parseInt(enemy_kills),
            parseInt(enemy_deaths),
            parseInt(enemy_assists),
            parseInt(team_gold),
            parseInt(enemy_gold),
            dragon_acquisition
        );

        const winProbPercent = Math.round(prediction.win_probability * 100 * 100) / 100;

        res.json({
            success: true,
            win_probability: winProbPercent,
            message: `Your team has a ${winProbPercent}% chance of winning!`,
            note: 'Prediction from trained Logistic Regression model (JavaScript implementation)',
            calculated_stats: {
                team_kda: Math.round(prediction.features.team_kda * 100) / 100,
                enemy_kda: Math.round(prediction.features.enemy_kda * 100) / 100,
                gold_difference: prediction.features.gold_diff,
                gold_per_kill: Math.round(prediction.features.gold_per_kill),
                dragon_advantage: dragon_acquisition
            },
            model_info: {
                accuracy: 0.701,
                algorithm: 'Logistic Regression',
                raw_probability: Math.round(prediction.win_probability * 10000) / 10000
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            note: 'Error in ML model prediction'
        });
    }
});

app.get('/api/health', (req, res) => {
    try {
        res.json({
            status: 'healthy',
            mode: 'pure javascript ml model',
            runtime: 'Node.js',
            version: process.version,
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            timestamp: new Date().toISOString(),
            note: 'Running trained ML model natively in JavaScript',
            model_info: {
                accuracy: 0.701,
                algorithm: 'Logistic Regression with Standard Scaler',
                implementation: 'Native JavaScript (no Python dependencies)'
            }
        });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            error: error.message
        });
    }
});

// Catch all for API routes
app.get('/api/*', (req, res) => {
    res.status(404).json({
        error: 'API endpoint not found',
        available_endpoints: ['/api/predict', '/api/health', '/api/test']
    });
});

// For Vercel serverless functions
module.exports = app;

// For local development
if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`LoL Win Predictor API running on port ${PORT}`);
    });
}