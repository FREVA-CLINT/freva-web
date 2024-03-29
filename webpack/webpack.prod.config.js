const path = require("path");

const webpack = require("webpack");

const mode = "production";
const entry = path.resolve("./assets/js/index");
const plugins = [
  // removes a lot of debugging code in React
  new webpack.DefinePlugin({
    "process.env": {
      NODE_ENV: JSON.stringify("production"),
    },
  }),
];

module.exports = function getProdConfig() {
  return {
    mode,
    entry,
    resolve: { extensions: [".js"] },
    plugins,
  };
};
