const axios = require('axios');

class Trading {
    constructor() {
        this.description = {
            displayName: 'Trading Bot',
            name: 'tradingBot',
            icon: 'file:trading.svg',
            group: ['transform'],
            version: 1,
            description: 'Execute Put or Call trades',
            defaults: {
                name: 'Trading Bot',
            },
            inputs: ['main'],
            outputs: ['main'],
            properties: [
                {
                    displayName: 'API URL',
                    name: 'apiUrl',
                    type: 'string',
                    default: 'http://localhost:5000',
                    required: true,
                    description: 'Trading API server URL',
                },
                {
                    displayName: 'Action',
                    name: 'action',
                    type: 'options',
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
                    description: 'Choose Put or Call',
                },
                {
                    displayName: 'Trading Pair',
                    name: 'pair',
                    type: 'string',
                    default: 'EURUSD',
                    required: true,
                    description: 'Trading pair (e.g., EURUSD, GBPUSD)',
                },
                {
                    displayName: 'Amount',
                    name: 'amount',
                    type: 'number',
                    default: 1,
                    required: true,
                    description: 'Trade amount in dollars',
                },
                {
                    displayName: 'Duration (minutes)',
                    name: 'duration',
                    type: 'number',
                    default: 1,
                    required: true,
                    description: 'Trade duration in minutes',
                },
                {
                    displayName: 'Email',
                    name: 'email',
                    type: 'string',
                    default: '',
                    required: true,
                    description: 'IQ Option account email',
                },
                {
                    displayName: 'Password',
                    name: 'password',
                    type: 'string',
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
                    description: 'Account type to use',
                },
            ],
        };
    }

    async execute() {
        const items = this.getInputData();
        const returnData = [];

        for (let i = 0; i < items.length; i++) {
            const apiUrl = this.getNodeParameter('apiUrl', i);
            const action = this.getNodeParameter('action', i);
            const pair = this.getNodeParameter('pair', i);
            const amount = this.getNodeParameter('amount', i);
            const duration = this.getNodeParameter('duration', i);
            const email = this.getNodeParameter('email', i);
            const password = this.getNodeParameter('password', i);
            const accountType = this.getNodeParameter('accountType', i);

            try {
                // Call the trading API
                const response = await axios.post(`${apiUrl}/trade`, {
                    email: email,
                    password: password,
                    action: action,
                    pair: pair,
                    amount: amount,
                    duration: duration,
                    accountType: accountType,
                }, {
                    timeout: (duration * 60 + 30) * 1000, // Wait for trade to complete
                });

                returnData.push({
                    json: {
                        ...response.data,
                        timestamp: new Date().toISOString(),
                    }
                });
            } catch (error) {
                returnData.push({
                    json: {
                        success: false,
                        error: error.message,
                        details: error.response?.data || null,
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
