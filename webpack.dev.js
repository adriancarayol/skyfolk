const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common[0], common[1], {
	context: __dirname,
	mode: 'development',
	devtool: 'inline-source-map',
	devServer: {
		contentBase: './skyfolk/static/dist',
	}
});