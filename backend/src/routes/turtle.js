const express = require('express');
const router = express.Router();
const agentService = require('../services/agentService');

/**
 * GET /api/turtle/:id
 * Kaplumbağa bilgisini getir
 */
router.get('/:id', async (req, res) => {
    try {
        const { id } = req.params;

        if (!id) {
            return res.status(400).json({ error: 'Turtle ID is required' });
        }

        const turtle = await agentService.getTurtleFromDatabase(id);

        res.status(200).json({
            success: true,
            turtle
        });

    } catch (error) {
        console.error('Error fetching turtle:', error.message);
        res.status(500).json({
            error: 'Failed to fetch turtle',
            message: error.message
        });
    }
});

/**
 * GET /api/turtle
 * Tüm kaplumbağaları listele (filtreleme seçeneği ile)
 */
router.get('/', async (req, res) => {
    try {
        const { location, species, limit = 50, offset = 0 } = req.query;

        const filters = {
            limit: parseInt(limit),
            offset: parseInt(offset)
        };

        if (location) filters.location = location;
        if (species) filters.species = species;

        const turtles = await agentService.getAllTurtles(filters);

        res.status(200).json({
            success: true,
            count: turtles.length,
            turtles
        });

    } catch (error) {
        console.error('Error fetching turtles:', error.message);
        res.status(500).json({
            error: 'Failed to fetch turtles',
            message: error.message
        });
    }
});

/**
 * PUT /api/turtle/:id
 * Kaplumbağa bilgisini güncelle
 */
router.put('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const updateData = req.body;

        if (!id) {
            return res.status(400).json({ error: 'Turtle ID is required' });
        }

        const updatedTurtle = await agentService.updateTurtleInDatabase(id, updateData);

        res.status(200).json({
            success: true,
            message: 'Turtle updated successfully',
            turtle: updatedTurtle
        });

    } catch (error) {
        console.error('Error updating turtle:', error.message);
        res.status(500).json({
            error: 'Failed to update turtle',
            message: error.message
        });
    }
});

module.exports = router;
