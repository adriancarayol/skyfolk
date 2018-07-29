const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common[0], common[1], {
	mode: 'production',
});