const axios = require('axios');

class Trading {
    constructor() {
        this.description = {
            displayName: 'IQOption AI Trading Bot',
            name: 'iqOptionTradingBot',
            icon: 'file:trading.svg',
            group: ['transform'],
            version: 2,
            description: 'AI-powered binary options trading with risk management - FIXED VERSION',
            defaults: {
                name: 'IQOption AI Trading Bot',
            },
            inputs: ['main'],
            outputs: ['main'],
            credentials: [
                {
                    name: 'iqOptionApi',
                    required: true,
                },
            ],
            properties: [
                {
                    displayName: 'Operation',
                    name: 'operation',
                    type: 'options',
                    options: [
                        {
                            name: 'Execute Trade',
                            value: 'trade',
                        },
                        {
                            name: 'Get Status',
                            value: 'status',
                        },
                        {
                            name: 'Reset State',
                            value: 'reset',
                        },
                    ],
                    default: 'trade',
                    description: 'Operation to perform',
                },
                {
                    displayName: 'API URL',
                    name: 'apiUrl',
                    type: 'string',
                    default: 'http://localhost:5000',
                    required: true,
                    description: 'Trading API server URL',
                },
                // Trade-specific fields
                {
                    displayName: 'Action',
                    name: 'action',
                    type: 'options',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    options: [
                        {
                            name: 'Call',
                            value: 'call',
                        },
                        {
                            name: 'Put',
                            value: 'put',
                        },
                    ],
                    default: 'call',
                    description: 'Trade direction: Call (up) or Put (down)',
                },
                {
                    displayName: 'Trading Pair',
                    name: 'pair',
                    type: 'string',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    default: 'AUDCHF-OTC',
                    required: true,
                    description: 'Trading pair (e.g., EURUSD, GBPUSD, AUDCHF-OTC)',
                },
                {
                    displayName: 'Confidence',
                    name: 'confidence',
                    type: 'number',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    default: 75,
                    typeOptions: {
                        minValue: 60,
                        maxValue: 100,
                    },
                    description: 'AI confidence level (60-100). Affects trade sizing and duration.',
                },
                {
                    displayName: 'Amount (Optional)',
                    name: 'amount',
                    type: 'number',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    default: 0,
                    description: 'Trade amount in dollars. Leave 0 for auto-calculation based on confidence and Martingale',
                },
                {
                    displayName: 'Duration (Optional)',
                    name: 'duration',
                    type: 'number',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    default: 0,
                    description: 'Trade duration in minutes. Leave 0 for auto-calculation based on confidence',
                },
                {
                    displayName: 'Account Type',
                    name: 'accountType',
                    type: 'options',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    options: [
                        {
                            name: 'Demo',
                            value: 'demo',
                        },
                        {
                            name: 'Real',
                            value: 'real',
                        },
                    ],
                    default: 'demo',
                    description: 'Account type to use (ALWAYS start with Demo)',
                },
                // Reset operation fields
                {
                    displayName: 'Reset Type',
                    name: 'resetType',
                    type: 'options',
                    displayOptions: {
                        show: {
                            operation: ['reset'],
                        },
                    },
                    options: [
                        {
                            name: 'Daily Stats',
                            value: 'daily',
                        },
                        {
                            name: 'Martingale Level',
                            value: 'martingale',
                        },
                        {
                            name: 'Full Reset',
                            value: 'full',
                        },
                    ],
                    default: 'daily',
                    description: 'Type of reset to perform',
                },
            ],
        };
    }

    async execute() {
        const items = this.getInputData();
        const returnData = [];

        for (let i = 0; i < items.length; i++) {
            const operation = this.getNodeParameter('operation', i);
            const apiUrl = this.getNodeParameter('apiUrl', i);

            try {
                // Get credentials
                const credentials = await this.getCredentials('iqOptionApi', i);
                
                if (!credentials) {
                    throw new Error('IQOption credentials not configured');
                }

                if (operation === 'trade') {
                    // Execute trade operation
                    const action = this.getNodeParameter('action', i);
                    const pair = this.getNodeParameter('pair', i);
                    const confidence = this.getNodeParameter('confidence', i);
                    const amount = this.getNodeParameter('amount', i);
                    const duration = this.getNodeParameter('duration', i);
                    const accountType = this.getNodeParameter('accountType', i);

                    // Validate confidence range
                    if (confidence < 60 || confidence > 100) {
                        throw new Error('Confidence must be between 60 and 100');
                    }

                    // Build request payload with credentials
                    const payload = {
                        email: credentials.email,
                        password: credentials.password,
                        action: action,
                        pair: pair,
                        confidence: confidence,
                        accountType: accountType,
                    };

                    // Only include amount and duration if provided (> 0)
                    if (amount > 0) {
                        payload.amount = amount;
                    }
                    if (duration > 0) {
                        payload.duration = duration;
                    }

                    // Calculate timeout based on duration (or default 5 min if auto)
                    const estimatedDuration = duration > 0 ? duration : 5;
                    const timeout = (estimatedDuration * 60 + 30) * 1000;

                    console.log(`[n8n Trading Node] Executing ${action.toUpperCase()} trade on ${pair} with ${confidence}% confidence`);

                    const response = await axios.post(`${apiUrl}/trade`, payload, {
                        timeout: timeout,
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    // Enhanced response validation
                    if (response.data && response.data.success) {
                        console.log(`[n8n Trading Node] Trade successful: ${response.data.result} with profit $${response.data.profit}`);
                    } else {
                        console.warn(`[n8n Trading Node] Trade completed but may have failed: ${response.data?.error || 'Unknown status'}`);
                    }

                    returnData.push({
                        json: {
                            ...response.data,
                            nodeTimestamp: new Date().toISOString(),
                            nodeVersion: '2.0-fixed',
                        }
                    });

                } else if (operation === 'status') {
                    // Get trading status
                    console.log('[n8n Trading Node] Fetching trading status');

                    const response = await axios.get(`${apiUrl}/status`, {
                        timeout: 10000,
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    returnData.push({
                        json: {
                            ...response.data,
                            nodeTimestamp: new Date().toISOString(),
                            nodeVersion: '2.0-fixed',
                        }
                    });

                } else if (operation === 'reset') {
                    // Reset trading state
                    const resetType = this.getNodeParameter('resetType', i);

                    console.log(`[n8n Trading Node] Resetting state: ${resetType}`);

                    const response = await axios.post(`${apiUrl}/reset`, {
                        type: resetType,
                    }, {
                        timeout: 10000,
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    returnData.push({
                        json: {
                            ...response.data,
                            nodeTimestamp: new Date().toISOString(),
                            nodeVersion: '2.0-fixed',
                        }
                    });
                }

            } catch (error) {
                console.error(`[n8n Trading Node] Error: ${error.message}`);

                // Enhanced error handling
                let errorDetails = {
                    success: false,
                    operation: operation,
                    error: error.message,
                    timestamp: new Date().toISOString(),
                    nodeVersion: '2.0-fixed',
                };

                // Add more details for different error types
                if (error.response) {
                    // HTTP error
                    errorDetails.statusCode = error.response.status;
                    errorDetails.statusText = error.response.statusText;
                    errorDetails.errorDetails = error.response.data;
                } else if (error.code === 'ECONNREFUSED') {
                    errorDetails.error = 'Cannot connect to API server. Please ensure the API is running.';
                    errorDetails.suggestion = 'Start the API with: python trading_api_fixed.py';
                } else if (error.code === 'ETIMEDOUT') {
                    errorDetails.error = 'Request timeout. Trade may still be processing.';
                    errorDetails.suggestion = 'Check API logs or try again later.';
                }

                returnData.push({
                    json: errorDetails,
                });
            }
        }

        return [returnData];
    }
}

module.exports = {
    Trading,
};