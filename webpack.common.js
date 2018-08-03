const path = require('path');
const glob = require('glob');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');


module.exports = [
    {
        context: __dirname,
        name: 'react',
        entry: toObject(glob.sync('./skyfolk-react/src/pages/**/*.js*')),
        output: {
            //where you want your compiled bundle to be stored
            path: path.resolve('./skyfolk/static/js/bundles/'),
            //naming convention webpack should use for your files
            filename: '[name]-[hash].js',
        },
        plugins: [
            //tells webpack where to store data about your bundles.
            new BundleTracker({
                filename: './webpack-stats.json'
            }),
            //makes jQuery available in every module
            new webpack.ProvidePlugin({
                $: 'jquery',
                jQuery: 'jquery',
                'window.jQuery': 'jquery'
            }),
            new UglifyJSPlugin({})
        ],

        module: {
            rules: [
                //a regexp that tells webpack use the following loaders on all
                //.js and .jsx files
                {
                    test: /\.jsx?$/,
                    //we definitely don't want babel to transpile all the files in
                    //node_modules. That would take a long time.
                    exclude: /node_modules/,
                    //use the babel loader
                    loader: 'babel-loader',
                    query: {
                        //specify that we will be dealing with React code
                        "presets": ['react']
                    },
                    enforce: 'pre'
                },
            ]
        },
        resolve: {
            //tells webpack where to look for modules
            modules: ['node_modules'],
            //extensions that should be used to resolve modules
            extensions: ['.js', '.jsx']
        }
    },
    {

    }
    /*
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
    */
];

function toObject(paths) {
    var ret = {};

    paths.forEach(function(path) {
        // you can define entry names mapped to [name] here
        ret[path.split('/').slice(-1)[0]] = path;
    });

    return ret;
}