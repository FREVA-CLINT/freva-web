const path = require("path");

const BundleTracker = require("webpack-bundle-tracker");
const ESLintPlugin = require("eslint-webpack-plugin");
const Dotenv = require("dotenv-webpack");

module.exports = function getBaseConfig() {
  return {
    // context: path.resolve(__dirname, ".."),
    output: {
      path: path.resolve("./assets/bundles/"),
      filename: "[name]-[fullhash].js",
    },
    optimization: {
      moduleIds: "named",
    },
    plugins: [
      new BundleTracker({ filename: "./webpack-stats.json" }),
      new ESLintPlugin(),
      new Dotenv(),
    ],
    module: {
      rules: [
        {
          test: /\.js?$/,
          exclude: /node_modules/,
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", "@babel/preset-react"],
          },
        },
        {
          test: /\.json$/,
          use: ["json-loader"],
          type: "javascript/auto",
        },
        {
          test: /\.css$/,
          use: ["style-loader", "css-loader"],
        },
      ],
    },

    resolve: {
      extensions: ["", ".js", ".jsx", ".css", ".ts"],
    },
  };
};
