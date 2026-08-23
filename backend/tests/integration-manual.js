/**
 * Turtle-ID MAS End-to-End Integration Test
 * 
 * SOLID mimarısındaki 4 ajanın (Gatekeeper, Biolytics, Matching, Reporter)
 * tamamının birlikte çalışmasını test eder
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configuration
const BASE_URL = 'http://localhost:3000';
const IMAGE_ANALYSIS_URL = 'http://localhost:5000';
const DATABASE_URL = 'http://localhost:5001';

// Test utilities
const logger = {
    success: (msg) => console.log(`✅ ${msg}`),
    error: (msg) => console.error(`❌ ${msg}`),
    info: (msg) => console.log(`ℹ️  ${msg}`),
    warn: (msg) => console.warn(`⚠️  ${msg}`)
};

// Mock image data (base64 encoded small valid PNG)
const MOCK_IMAGE_BASE64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';

/**
 * Test 1: Gatekeeper Agent - Metadata Validation
 */
async function testGatekeeperValidation() {
    logger.info('TEST 1: Gatekeeper Agent - Metadata Validation');
    
    try {
        const validationData = {
            imageBase64: MOCK_IMAGE_BASE64,
            timestamp: new Date().toISOString(),
            location: {
                latitude: 36.7138,
                longitude: 31.2327,
                accuracy: 10.5
            },
            observer: {
                name: 'Dr. John Doe',
                email: 'john@example.com',
                organization: 'Marine Research Institute'
            },
            conditions: {
                waterTemperature: 24.5,
                weather: 'sunny',
                waterClarity: 'clear'
            }
        };

        const response = await axios.post(
            `${BASE_URL}/api/validation/validate`,
            validationData
        );

        if (response.status === 200 && response.data.success) {
            logger.success('Gatekeeper validation passed');
            return response.data.validated_metadata;
        } else {
            throw new Error(`Validation failed: ${JSON.stringify(response.data)}`);
        }
    } catch (error) {
        logger.error(`Gatekeeper validation failed: ${error.message}`);
        throw error;
    }
}

/**
 * Test 2: Biolytics Agent - Auto-detect Species
 */
async function testBiolyticsAutoDetect() {
    logger.info('TEST 2: Biolytics Agent - Auto-detect Species');
    
    try {
        const analysisData = {
            image: MOCK_IMAGE_BASE64
        };

        const response = await axios.post(
            `${IMAGE_ANALYSIS_URL}/api/biolytics/auto-detect`,
            analysisData,
            {
                headers: {
                    'X-Request-ID': 'test-' + Date.now()
                }
            }
        );

        if (response.status === 200 && response.data.success) {
            logger.success('Biolytics auto-detect passed');
            return {
                species: response.data.detection.analysis.species,
                biometricCode: response.data.detection.analysis.biometric_code,
                confidence: response.data.detection.analysis.confidence,
                extractionMethod: response.data.detection.analysis.extraction_method
            };
        } else {
            throw new Error(`Auto-detect failed: ${JSON.stringify(response.data)}`);
        }
    } catch (error) {
        logger.error(`Biolytics auto-detect failed: ${error.message}`);
        throw error;
    }
}

/**
 * Test 3: Matching Agent - Find Similar Records
 */
async function testMatchingAgent(biometricCode) {
    logger.info('TEST 3: Matching Agent - Find Similar Records');
    
    try {
        const matchingData = {
            biometricCode: biometricCode,
            matchingCriteria: {
                threshold: 0.9,
                topN: 5,
                method: 'hamming'
            }
        };

        const response = await axios.post(
            `${BASE_URL}/api/matching/find`,
            matchingData
        );

        if (response.status === 200 && response.data.success) {
            logger.success(`Matching completed: ${response.data.matching_result.classification}`);
            return {
                classification: response.data.matching_result.classification,
                confidence: response.data.matching_result.confidence || 0,
                matches: response.data.matching_result.matches,
                topMatch: response.data.matching_result.topMatch
            };
        } else {
            throw new Error(`Matching failed: ${JSON.stringify(response.data)}`);
        }
    } catch (error) {
        logger.error(`Matching agent failed: ${error.message}`);
        throw error;
    }
}

/**
 * Test 4: Reporter Agent - Generate DEKAMER Report
 */
async function testReporterAgent(analysisData, matchingData) {
    logger.info('TEST 4: Reporter Agent - Generate DEKAMER Report');
    
    try {
        const reportData = {
            format: 'json',
            analysisData: {
                analysis: {
                    species: analysisData.species,
                    confidence: analysisData.confidence
                },
                biometric_code: analysisData.biometricCode,
                extraction_method: analysisData.extractionMethod,
                quality_score: 0.95,
                metadata: {
                    timestamp: new Date().toISOString(),
                    location: {
                        latitude: 36.7138,
                        longitude: 31.2327,
                        accuracy: 10.5
                    },
                    observer: {
                        name: 'Dr. John Doe',
                        email: 'john@example.com'
                    },
                    conditions: {
                        waterTemperature: 24.5
                    }
                },
                measurements: {
                    shell_length: 85.5,
                    shell_width: 75.0,
                    weight: 150
                },
                health: {
                    wounds: [],
                    diseases: [],
                    parasites: [],
                    condition: 'GOOD'
                }
            },
            matchingData: {
                classification: matchingData.classification,
                confidence: matchingData.confidence,
                threshold: 0.9,
                topMatch: matchingData.topMatch
            }
        };

        const response = await axios.post(
            `${BASE_URL}/api/reporting/generate`,
            reportData
        );

        if (response.status === 200 && response.data.success) {
            logger.success('Reporter generated DEKAMER report');
            
            // Save report
            const reportPath = path.join(__dirname, `test-report-${Date.now()}.json`);
            fs.writeFileSync(reportPath, JSON.stringify(response.data.report, null, 2));
            logger.info(`Report saved to: ${reportPath}`);
            
            return response.data.report;
        } else {
            throw new Error(`Report generation failed: ${JSON.stringify(response.data)}`);
        }
    } catch (error) {
        logger.error(`Reporter agent failed: ${error.message}`);
        throw error;
    }
}

/**
 * Test Agent Health Checks
 */
async function testAgentHealthChecks() {
    logger.info('Testing Agent Health Checks...');
    
    const endpoints = [
        { name: 'Gatekeeper Agent', url: `${BASE_URL}/api/validation/health` },
        { name: 'Biolytics Agent', url: `${IMAGE_ANALYSIS_URL}/api/biolytics/health` },
        { name: 'Matching Agent', url: `${BASE_URL}/api/matching/health` },
        { name: 'Reporter Agent', url: `${BASE_URL}/api/reporting/health` },
        { name: 'Database Agent', url: `${DATABASE_URL}/health` }
    ];

    const healthResults = {};

    for (const endpoint of endpoints) {
        try {
            const response = await axios.get(endpoint.url, { timeout: 5000 });
            if (response.status === 200) {
                healthResults[endpoint.name] = 'healthy ✅';
                logger.success(`${endpoint.name}: healthy`);
            } else {
                healthResults[endpoint.name] = 'unhealthy ❌';
                logger.error(`${endpoint.name}: unhealthy`);
            }
        } catch (error) {
            healthResults[endpoint.name] = `failed (${error.code || 'unknown'})`;
            logger.error(`${endpoint.name}: ${error.message}`);
        }
    }

    return healthResults;
}

/**
 * Main Test Runner
 */
async function runIntegrationTests() {
    console.log('\n');
    console.log('╔════════════════════════════════════════════════════════════════╗');
    console.log('║  Turtle-ID MAS End-to-End Integration Test                     ║');
    console.log('║  SOLID Architecture with 4 Specialized Agents                  ║');
    console.log('╚════════════════════════════════════════════════════════════════╝');
    console.log('\n');

    try {
        // Step 0: Health checks
        logger.info('=== STEP 0: Agent Health Checks ===');
        const healthResults = await testAgentHealthChecks();
        console.table(healthResults);
        console.log('\n');

        // Step 1: Gatekeeper validation
        logger.info('=== STEP 1: Gatekeeper Agent ===');
        const validatedMetadata = await testGatekeeperValidation();
        console.log('Validated metadata:', JSON.stringify(validatedMetadata, null, 2));
        console.log('\n');

        // Step 2: Biolytics analysis
        logger.info('=== STEP 2: Biolytics Agent ===');
        const biolyticsResult = await testBiolyticsAutoDetect();
        console.log('Analysis result:', JSON.stringify(biolyticsResult, null, 2));
        console.log('\n');

        // Step 3: Matching
        logger.info('=== STEP 3: Matching Agent ===');
        const matchingResult = await testMatchingAgent(biolyticsResult.biometricCode);
        console.log('Matching result:', JSON.stringify(matchingResult, null, 2));
        console.log('\n');

        // Step 4: Reporting
        logger.info('=== STEP 4: Reporter Agent ===');
        const report = await testReporterAgent(biolyticsResult, matchingResult);
        console.log('Report generated:', JSON.stringify(report, null, 2).substring(0, 500) + '...');
        console.log('\n');

        // Summary
        console.log('╔════════════════════════════════════════════════════════════════╗');
        console.log('║                    TEST SUMMARY                                ║');
        console.log('╚════════════════════════════════════════════════════════════════╝');
        console.log('\n');
        console.log('✅ All integration tests passed!');
        console.log('\nWorkflow Summary:');
        console.log('  1. ✅ Gatekeeper Agent validated metadata');
        console.log('  2. ✅ Biolytics Agent identified species');
        console.log('  3. ✅ Matching Agent compared biometrics');
        console.log('  4. ✅ Reporter Agent generated DEKAMER report');
        console.log('\nSystem Status: FULLY OPERATIONAL 🎉');
        console.log('\n');

    } catch (error) {
        console.log('\n');
        console.log('╔════════════════════════════════════════════════════════════════╗');
        console.log('║                    TEST FAILED                                 ║');
        console.log('╚════════════════════════════════════════════════════════════════╝');
        console.log('\n');
        logger.error(`Integration test failed at: ${error.message}`);
        console.log('\nTroubleshooting:');
        console.log('  1. Ensure all agents are running:');
        console.log('     - Backend Coordinator: http://localhost:3000');
        console.log('     - Image Analysis Agent: http://localhost:5000');
        console.log('     - Database Agent: http://localhost:5001');
        console.log('  2. Check agent logs for details');
        console.log('  3. Verify network connectivity between agents');
        console.log('\n');
        process.exit(1);
    }
}

// Run tests
if (require.main === module) {
    runIntegrationTests()
        .then(() => process.exit(0))
        .catch((error) => {
            console.error('Fatal error:', error);
            process.exit(1);
        });
}

module.exports = {
    testGatekeeperValidation,
    testBiolyticsAutoDetect,
    testMatchingAgent,
    testReporterAgent,
    testAgentHealthChecks,
    runIntegrationTests
};
