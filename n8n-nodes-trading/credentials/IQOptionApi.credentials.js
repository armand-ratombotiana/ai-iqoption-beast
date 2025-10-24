class IQOptionApi {
    constructor() {
        this.name = 'iqOptionApi';
        this.displayName = 'IQOption API';
        this.documentationUrl = 'https://iqoption.com';
        this.properties = [
            {
                displayName: 'Email',
                name: 'email',
                type: 'string',
                default: '',
                required: true,
                description: 'Your IQOption account email',
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
                description: 'Your IQOption account password',
            },
        ];
    }
}

module.exports = {
    IQOptionApi,
};