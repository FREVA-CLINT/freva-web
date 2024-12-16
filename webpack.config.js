const { merge } = require("webpack-merge");

const baseConfig = require("./webpack/webpack.base.config");
const devConfig = require("./webpack/webpack.dev.config");
const prodConfig = require("./webpack/webpack.prod.config");
const webpack = require('webpack');

const Dotenv = require("dotenv-webpack");

let config;
if (["build", "dev"].includes(process.env.npm_lifecycle_event)) {
  config = merge(
    devConfig(),
    baseConfig(),
    { node: { __dirname: true } });
} else {
  // production
  config = merge(
    prodConfig(),
    baseConfig(),
    { node: { __dirname: true } });
}

module.exports = config;
