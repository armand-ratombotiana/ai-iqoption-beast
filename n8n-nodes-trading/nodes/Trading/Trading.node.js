const axios = require('axios');

class Trading {
    constructor() {
        this.description = {
            displayName: 'IQOption AI Trading Bot',
            name: 'iqOptionTradingBot',
            icon: 'file:trading.svg',
            group: ['transform'],
            version: 2,
            description: 'AI-powered binary options trading with risk management',
            defaults: {
                name: 'IQOption AI Trading Bot',
            },
            inputs: ['main'],
            outputs: ['main'],
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
                    default: 'EURUSD',
                    required: true,
                    description: 'Trading pair (e.g., EURUSD, GBPUSD, BTCUSD)',
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
                        minValue: 0,
                        maxValue: 100,
                    },
                    description: 'AI confidence level (0-100). Affects trade sizing and duration.',
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
                    displayName: 'Email',
                    name: 'email',
                    type: 'string',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    default: '',
                    required: true,
                    description: 'IQ Option account email',
                },
                {
                    displayName: 'Password',
                    name: 'password',
                    type: 'string',
                    displayOptions: {
                        show: {
                            operation: ['trade'],
                        },
                    },
                    typeOptions: {
                        password: true,
                    },
                    default: '',
                    required: true,
                    description: 'IQ Option account password',
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
                if (operation === 'trade') {
                    // Execute trade operation
                    const action = this.getNodeParameter('action', i);
                    const pair = this.getNodeParameter('pair', i);
                    const confidence = this.getNodeParameter('confidence', i);
                    const amount = this.getNodeParameter('amount', i);
                    const duration = this.getNodeParameter('duration', i);
                    const email = this.getNodeParameter('email', i);
                    const password = this.getNodeParameter('password', i);
                    const accountType = this.getNodeParameter('accountType', i);

                    // Build request payload
                    const payload = {
                        email: email,
                        password: password,
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
                    });

                    returnData.push({
                        json: {
                            ...response.data,
                            nodeTimestamp: new Date().toISOString(),
                        }
                    });

                } else if (operation === 'status') {
                    // Get trading status
                    console.log('[n8n Trading Node] Fetching trading status');

                    const response = await axios.get(`${apiUrl}/status`, {
                        timeout: 5000,
                    });

                    returnData.push({
                        json: {
                            ...response.data,
                            nodeTimestamp: new Date().toISOString(),
                        }
                    });

                } else if (operation === 'reset') {
                    // Reset trading state
                    const resetType = this.getNodeParameter('resetType', i);

                    console.log(`[n8n Trading Node] Resetting state: ${resetType}`);

                    const response = await axios.post(`${apiUrl}/reset`, {
                        type: resetType,
                    }, {
                        timeout: 5000,
                    });

                    returnData.push({
                        json: {
                            ...response.data,
                            nodeTimestamp: new Date().toISOString(),
                        }
                    });
                }

            } catch (error) {
                console.error(`[n8n Trading Node] Error: ${error.message}`);

                // Include detailed error information
                returnData.push({
                    json: {
                        success: false,
                        operation: operation,
                        error: error.message,
                        errorDetails: error.response?.data || null,
                        statusCode: error.response?.status || null,
                        timestamp: new Date().toISOString(),
                    },
                });
            }
        }

        return [returnData];
    }
}

module.exports = {
    Trading,
};
