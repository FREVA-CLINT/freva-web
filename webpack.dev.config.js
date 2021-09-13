var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

var config = require('./webpack.base.config.js');
config.mode = 'development'
config.entry = [
  'webpack-dev-server/client?http://localhost:8080',
  'webpack/hot/only-dev-server',
  './assets/js/index'
];

// override django's STATIC_URL for webpack bundles
config.output.publicPath = 'http://localhost:8080/assets/bundles/';

// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoEmitOnErrorsPlugin(),
  new BundleTracker({filename: './webpack-stats.json'})
]);

// Add a loader for JSX files with react-hot enabled
config.module.rules.push(
  { test: /\.js?$/,
    exclude: /node_modules/,
    loader: 'babel-loader',
    options: {
      //presets: ['env', 'react', 'react-hmre', 'stage-0', 'babel-polyfill']
      presets: ["@babel/preset-env", "@babel/preset-react"]
    }
  } // to transform JSX into JS
);

module.exports = config;
