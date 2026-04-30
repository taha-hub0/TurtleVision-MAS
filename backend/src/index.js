const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();

const agentService = require('./services/agentService');
const identificationRoutes = require('./routes/identification');
const turtleRoutes = require('./routes/turtle');
const healthRoutes = require('./routes/health');
const validationRoutes = require('./routes/validation');
const matchingRoutes = require('./routes/matching');
const reportingRoutes = require('./routes/reporting');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

// Logger middleware
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
});

// Routes
app.use('/api/health', healthRoutes);
app.use('/api/turtle', turtleRoutes);
app.use('/api/identification', identificationRoutes);
app.use('/api/validation', validationRoutes);
app.use('/api/matching', matchingRoutes);
app.use('/api/reporting', reportingRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(err.status || 500).json({
        error: err.message || 'Internal Server Error',
        timestamp: new Date().toISOString()
    });
});

// Initialize agents
const initializeAgents = async () => {
    try {
        console.log('Initializing Multi-Agent System...');

        // Check Image Analysis Agent
        const imageAgentHealthy = await agentService.checkImageAnalysisAgent();
        console.log(`Image Analysis Agent: ${imageAgentHealthy ? 'OK' : 'FAILED'}`);

        // Check Database Agent
        const dbAgentHealthy = await agentService.checkDatabaseAgent();
        console.log(`Database Agent: ${dbAgentHealthy ? 'OK' : 'FAILED'}`);

        if (imageAgentHealthy && dbAgentHealthy) {
            console.log('All agents initialized successfully!');
        } else {
            console.warn('Some agents are not responding. System will retry.');
        }
    } catch (error) {
        console.error('Failed to initialize agents:', error);
    }
};

// Start server
app.listen(PORT, async () => {
    console.log(`
  ╔═══════════════════════════════════════════╗
  ║   Turtle-ID Coordinator Agent Started     ║
  ║   Port: ${PORT}                            ║
  ╚═══════════════════════════════════════════╝
  `);

    await initializeAgents();
});

module.exports = app;
