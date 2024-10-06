// .eslintrc.js
module.exports = {
    env: {
        browser: true,
        es6: true,
        node: true,
        mocha: true,
    },
    extends: ['eslint:recommended'],
    parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module',
    },
    rules: {
        // Customize your linting rules
        'no-unused-vars': ['warn'],
        'no-console': 'off',
    },
};
