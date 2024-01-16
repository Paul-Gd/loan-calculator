module.exports = {
  modifyWebpackConfig({
    webpackConfig, // the created webpack config
  }) {
    return {
      ...webpackConfig,
      // chartjs has a bug so tree shaking does not work: https://github.com/chartjs/Chart.js/pull/10504
      performance: { maxAssetSize: 1000000, maxEntrypointSize: 1000000 },
    };
  },
};
