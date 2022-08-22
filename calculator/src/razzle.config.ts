export const OPTIONS = {
  options: {
    staticExport: {
      parallel: 5, // how many pages to render at a time
      routesExport: "routes",
      renderExport: "render",
      scriptInline: true,
      windowRoutesVariable: "RAZZLE_STATIC_ROUTES",
      windowRoutesDataVariable: "RAZZLE_STATIC_DATA_ROUTES",
    },
  },
};
