const path = require('path');
const glob = require('glob');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');


module.exports = [


    {
        context: __dirname,
        name: 'css',
        entry: {
            'bundle.min.css': [
              path.resolve('./skyfolk/static/css/core.css'),
              path.resolve('./skyfolk/static/css/profile.css'),
              path.resolve('./skyfolk/static/css/buscar.css'),
              path.resolve('./skyfolk/static/css/comentarios.css'),
              path.resolve('./skyfolk/static/colorbox/colorbox.css'),
              path.resolve('./skyfolk/static/dist/sweetalert.css'),
              path.resolve('./skyfolk/static/emoji/css/textarea_find_emoji.css'),
              path.resolve('./skyfolk/static/themes/google/google.css'),
            ],
          },
          output: {
            filename: '[name]',
            path: path.resolve('./skyfolk/static/dist/css/'),
          },
          module: {
            rules: [
              {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                  fallback: 'style-loader',
                  use: {loader: 'css-loader', options: { minimize: true }}
                }),
              },
              {
                test: /\.(png|woff|woff2|eot|ttf|svg|gif|jpeg|jpg)$/,
                loader: 'url-loader?limit=100000'
            }
            ],
          },
      plugins: [
        new ExtractTextPlugin("bundle.min.css"),
      ]
    }

];

function toObject(paths) {
    var ret = {};

    paths.forEach(function(path) {
        // you can define entry names mapped to [name] here
        ret[path.split('/').slice(-1)[0]] = path;
    });

    return ret;
}