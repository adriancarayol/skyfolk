//require our dependencies
var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var glob = require('glob');
var UglifyJSPlugin = require('uglifyjs-webpack-plugin');
var ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = [
    {
        //the base directory (absolute path) for resolving the entry option
        context: __dirname,
        name: "react",
        //the entry point we created earlier. Note that './' means
        //your current directory. You don't have to specify the extension  now,
        //because you will specify extensions later in the `resolve` section
        entry: toObject(glob.sync('./skyfolk-react/src/pages/**/*.js*')),

        output: {
            //where you want your compiled bundle to be stored
            path: path.resolve('./skyfolk/static/js/bundles/'),
            //naming convention webpack should use for your files
            filename: '[name]-[hash].js',
        },

        plugins: [
            //tells webpack where to store data about your bundles.
            new BundleTracker({filename: './webpack-stats.json'}),
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
        context: __dirname,
        name: "react",
        //the entry point we created earlier. Note that './' means
        //your current directory. You don't have to specify the extension  now,
        //because you will specify extensions later in the `resolve` section
        entry: {
            'bundle.min.css': [
                path.resolve('./skyfolk/static/css/core.css'),
                path.resolve('./skyfolk/static/css/buscar.css'),
            ]
        },
        output: {
            //where you want your compiled bundle to be stored
            path: path.resolve('./skyfolk/static/css/'),
            //naming convention webpack should use for your files
            filename: '[name].css',
        },
        watch: true,
        module: {
            rules: [
                {
                    test: /\.css$/,
                    use: ExtractTextPlugin.extract({
                        fallback: 'style-loader',
                        use: [
                            { loader: 'css-loader', options: { minimize: true } },
                        ]
                    })
                },
                { test: /\.(png|woff|woff2|eot|ttf|svg)$/, loader: 'url-loader?limit=100000' },
                { test: /\.(png|jpg|svg)$/, loader: 'file-loader' },
            ],
        },
        plugins: [
            new ExtractTextPlugin("bundle.min.css"),
        ]
    }
];

function toObject(paths) {
    var ret = {};

    paths.forEach(function (path) {
        // you can define entry names mapped to [name] here
        ret[path.split('/').slice(-1)[0]] = path;
    });

    return ret;
}