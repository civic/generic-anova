const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  entry: './src/js/app.js',
  output: {
    // 出力するファイル名
    filename: 'bundle.js',
    path: path.join(__dirname, '../static')
  },
  devServer: {
    host: '0.0.0.0',
    contentBase: (__dirname, '../static'),
    proxy: {
      '/api': {target: 'http://localhost:8000'},
      '/sse': {target: 'http://localhost:8000'},
    }
  },
  devtool: 'source-map',
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.esm.js'
    }
  },
  plugins: [
    new CopyWebpackPlugin([
      { from: 'src/index.html' },
      { from: 'assets'}
    ])
  ]
};
