const axios = require('axios');
const mysql = require('mysql2/promise');

class AgentService {
    constructor() {
        this.imageAgentUrl = process.env.IMAGE_AGENT_URL || 'http://localhost:5000';
        this.dbAgentUrl = process.env.DB_AGENT_URL || 'http://localhost:5001';
        this.imageAgentTimeout = parseInt(process.env.IMAGE_AGENT_TIMEOUT) || 30000;
        this.dbAgentTimeout = parseInt(process.env.DB_AGENT_TIMEOUT) || 10000;
    }

    /**
     * Görüntü Analiz Agent'ı sağlık kontrolü
     */
    async checkImageAnalysisAgent() {
        try {
            const response = await axios.get(`${this.imageAgentUrl}/health`, {
                timeout: 5000
            });
            return response.status === 200;
        } catch (error) {
            console.error('Image Analysis Agent health check failed:', error.message);
            return false;
        }
    }

    /**
     * Veritabanı Agent'ı sağlık kontrolü
     */
    async checkDatabaseAgent() {
        try {
            const response = await axios.get(`${this.dbAgentUrl}/health`, {
                timeout: 5000
            });
            return response.status === 200;
        } catch (error) {
            console.error('Database Agent health check failed:', error.message);
            return false;
        }
    }

    /**
     * Kaplumbağa tanımlama görüntü analiz iste
     */
    async identifyTurtle(imageBase64, metadata = {}) {
        try {
            const response = await axios.post(
                `${this.imageAgentUrl}/api/analyze`,
                {
                    image: imageBase64,
                    metadata
                },
                { timeout: this.imageAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Image Analysis Agent error:', error.message);
            throw new Error(`Image analysis failed: ${error.message}`);
        }
    }

    /**
     * Veritabanına kaplumbağa bilgisi kaydet
     */
    async saveTurtleToDatabase(turtleData) {
        try {
            const response = await axios.post(
                `${this.dbAgentUrl}/api/turtle/save`,
                turtleData,
                { timeout: this.dbAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Database Agent error:', error.message);
            throw new Error(`Database save failed: ${error.message}`);
        }
    }

    /**
     * Veritabanından kaplumbağa bilgisi getir
     */
    async getTurtleFromDatabase(turtleId) {
        try {
            const response = await axios.get(
                `${this.dbAgentUrl}/api/turtle/${turtleId}`,
                { timeout: this.dbAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Database Agent error:', error.message);
            throw new Error(`Database fetch failed: ${error.message}`);
        }
    }

    /**
     * Tüm kaplumbağaları veritabanından getir
     */
    async getAllTurtles(filters = {}) {
        try {
            const response = await axios.get(
                `${this.dbAgentUrl}/api/turtles`,
                { params: filters, timeout: this.dbAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Database Agent error:', error.message);
            throw new Error(`Database query failed: ${error.message}`);
        }
    }

    /**
     * Kaplumbağa bilgisi güncelle
     */
    async updateTurtleInDatabase(turtleId, updateData) {
        try {
            const response = await axios.put(
                `${this.dbAgentUrl}/api/turtle/${turtleId}`,
                updateData,
                { timeout: this.dbAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Database Agent error:', error.message);
            throw new Error(`Database update failed: ${error.message}`);
        }
    }

    /**
     * Benzer kaplumbağaları ara
     */
    async findSimilarTurtles(imageAnalysisResult, threshold = 0.85) {
        try {
            const response = await axios.post(
                `${this.dbAgentUrl}/api/turtle/similarity-search`,
                {
                    imageFeatures: imageAnalysisResult.features,
                    threshold
                },
                { timeout: this.dbAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Similarity search failed:', error.message);
            throw new Error(`Similarity search failed: ${error.message}`);
        }
    }

    /**
     * Tüm kaplumbağaların biyometrik kodlarını getir (Matching Agent için)
     */
    async getAllTurtlesBiometrics() {
        try {
            const response = await axios.get(
                `${this.dbAgentUrl}/api/turtle/biometrics`,
                { timeout: this.dbAgentTimeout }
            );
            return response.data.biometrics || [];
        } catch (error) {
            console.error('Database Agent error:', error.message);
            throw new Error(`Failed to fetch biometrics: ${error.message}`);
        }
    }

    /**
     * Biolytics Agent (Görüntü Analiz) sağlık kontrolü
     */
    async checkBiolyticsAgent() {
        try {
            const response = await axios.get(
                `${this.imageAgentUrl}/api/biolytics/health`,
                { timeout: 5000 }
            );
            return response.status === 200;
        } catch (error) {
            console.error('Biolytics Agent health check failed:', error.message);
            return false;
        }
    }

    /**
     * Biolytics Agent ile görüntüyü analiz et
     */
    async analyzeTurtleWithBiolytics(imageBase64, strategy = null) {
        try {
            const response = await axios.post(
                `${this.imageAgentUrl}/api/biolytics/analyze`,
                {
                    image: imageBase64,
                    strategy
                },
                { timeout: this.imageAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Biolytics analysis failed:', error.message);
            throw new Error(`Biolytics analysis failed: ${error.message}`);
        }
    }

    /**
     * Otomatik tür bulma (Biolytics Auto-Detect)
     */
    async autoDetectSpecies(imageBase64) {
        try {
            const response = await axios.post(
                `${this.imageAgentUrl}/api/biolytics/auto-detect`,
                {
                    image: imageBase64
                },
                { timeout: this.imageAgentTimeout }
            );
            return response.data;
        } catch (error) {
            console.error('Auto-detect failed:', error.message);
            throw new Error(`Auto-detect failed: ${error.message}`);
        }
    }
}

module.exports = new AgentService();
