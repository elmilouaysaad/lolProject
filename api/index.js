// LoL Win Predictor API - JavaScript with Python ML Model
const express = require('express');
const cors = require('cors');
const path = require('path');
const { spawn } = require('child_process');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Function to call Python model service
function callPythonModel(teamKills, teamDeaths, teamAssists, 
                        enemyKills, enemyDeaths, enemyAssists,
                        teamGold, enemyGold, dragonAcquisition) {
    return new Promise((resolve, reject) => {
        // Use the model.py in the parent directory
        const pythonProcess = spawn('python', [
            path.join(__dirname, '..', 'model.py'),
            teamKills.toString(),
            teamDeaths.toString(),
            teamAssists.toString(),
            enemyKills.toString(),
            enemyDeaths.toString(),
            enemyAssists.toString(),
            teamGold.toString(),
            enemyGold.toString(),
            dragonAcquisition
        ]);

        let dataString = '';
        let errorString = '';

        pythonProcess.stdout.on('data', (data) => {
            dataString += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorString += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(dataString.trim());
                    resolve(result);
                } catch (e) {
                    reject(new Error(`Failed to parse Python output: ${e.message}\nOutput: ${dataString}`));
                }
            } else {
                reject(new Error(`Python process failed with code ${code}: ${errorString}`));
            }
        });

        pythonProcess.on('error', (error) => {
            reject(new Error(`Failed to start Python process: ${error.message}`));
        });
    });
}

// Routes
app.get('/', (req, res) => {
    res.json({
        status: 'LoL Win Predictor API is running',
        mode: 'Python ML Model Service',
        endpoints: ['/api/predict', '/api/health', '/api/test'],
        version: '5.0.0',
        note: 'Using Python scikit-learn model for predictions'
    });
});

app.get('/api', (req, res) => {
    res.json({
        status: 'LoL Win Predictor API is running',
        mode: 'Python ML Model Service', 
        endpoints: ['/api/predict', '/api/health', '/api/test'],
        version: '5.0.0',
        note: 'Using Python scikit-learn model for predictions'
    });
});

app.get('/api/test', (req, res) => {
    res.json({
        test: 'JavaScript API is working',
        route: '/api/test',
        domain: 'lol-project-gamma.vercel.app',
        runtime: 'Node.js + Python ML Model',
        timestamp: new Date().toISOString()
    });
});

app.post('/api/predict', async (req, res) => {
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

        // Call Python model service for prediction
        const prediction = await callPythonModel(
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

        if (prediction.success) {
            res.json({
                success: true,
                win_probability: prediction.win_probability,
                message: `Your team has a ${prediction.win_probability}% chance of winning!`,
                note: 'Prediction from Python scikit-learn model',
                calculated_stats: prediction.calculated_stats,
                model_info: prediction.model_info,
                prediction_label: prediction.prediction_label
            });
        } else {
            res.status(500).json({
                success: false,
                error: prediction.error
            });
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            note: 'Error calling Python ML model service'
        });
    }
});

app.get('/api/health', (req, res) => {
    try {
        res.json({
            status: 'healthy',
            mode: 'python ml model service',
            runtime: 'Node.js + Python',
            version: process.version,
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            timestamp: new Date().toISOString(),
            note: 'Running Node.js API with Python scikit-learn model'
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