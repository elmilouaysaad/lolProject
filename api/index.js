// LoL Win Predictor API - JavaScript Version
const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Simple rule-based prediction (same logic as Python version)
function simplePrediction(teamKills, teamDeaths, teamAssists, 
                         enemyKills, enemyDeaths, enemyAssists,
                         teamGold, enemyGold, dragonAcquisition) {
    // Calculate basic stats
    const teamKDA = (teamKills + teamAssists) / Math.max(1, teamDeaths);
    const enemyKDA = (enemyKills + enemyAssists) / Math.max(1, enemyDeaths);
    const goldDiff = teamGold - enemyGold;
    
    // Simple scoring system
    let score = 0;
    
    // KDA advantage (40% weight)
    if (teamKDA > enemyKDA) {
        score += 0.4 * Math.min(0.8, (teamKDA - enemyKDA) / 3.0);
    } else {
        score -= 0.4 * Math.min(0.8, (enemyKDA - teamKDA) / 3.0);
    }
    
    // Gold advantage (35% weight)
    if (goldDiff > 0) {
        score += 0.35 * Math.min(0.8, goldDiff / 15000);
    } else {
        score -= 0.35 * Math.min(0.8, Math.abs(goldDiff) / 15000);
    }
    
    // Dragon advantage (25% weight)
    if (dragonAcquisition.toLowerCase() === 'team') {
        score += 0.25;
    } else if (dragonAcquisition.toLowerCase() === 'enemy') {
        score -= 0.25;
    }
    
    // Convert to probability (50% base + score adjustment)
    let winProbability = 0.5 + score;
    winProbability = Math.max(0.05, Math.min(0.95, winProbability)); // Clamp between 5% and 95%
    
    return winProbability;
}

// Routes
app.get('/', (req, res) => {
    res.json({
        status: 'LoL Win Predictor API is running',
        mode: 'JavaScript Rule-Based Prediction',
        endpoints: ['/api/predict', '/api/health', '/api/test'],
        version: '2.0.0'
    });
});

app.get('/api', (req, res) => {
    res.json({
        status: 'LoL Win Predictor API is running',
        mode: 'JavaScript Rule-Based Prediction',
        endpoints: ['/api/predict', '/api/health', '/api/test'],
        version: '2.0.0'
    });
});

app.get('/api/test', (req, res) => {
    res.json({
        test: 'JavaScript API is working',
        route: '/api/test',
        domain: 'lol-project-gamma.vercel.app',
        runtime: 'Node.js',
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

        // Get prediction using simple rules
        const winProb = simplePrediction(
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

        res.json({
            success: true,
            win_probability: Math.round(winProb * 100 * 100) / 100, // Round to 2 decimal places
            message: `Your team has a ${Math.round(winProb * 100 * 100) / 100}% chance of winning!`,
            note: 'Prediction based on rule-based algorithm (JavaScript version)',
            calculated_stats: {
                team_kda: Math.round(((parseInt(team_kills) + parseInt(team_assists)) / Math.max(1, parseInt(team_deaths))) * 100) / 100,
                enemy_kda: Math.round(((parseInt(enemy_kills) + parseInt(enemy_assists)) / Math.max(1, parseInt(enemy_deaths))) * 100) / 100,
                gold_difference: parseInt(team_gold) - parseInt(enemy_gold),
                dragon_advantage: dragon_acquisition
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.get('/api/health', (req, res) => {
    try {
        res.json({
            status: 'healthy',
            mode: 'javascript',
            runtime: 'Node.js',
            version: process.version,
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            timestamp: new Date().toISOString(),
            note: 'Running JavaScript API without heavy dependencies'
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