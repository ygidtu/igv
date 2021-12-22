module.exports = {
    lintOnSave: true, //禁用eslint
    publicPath: 'static',  // static
    outputDir: "./dist",
    runtimeCompiler: true,
    productionSourceMap: false,
    configureWebpack:{
        performance: {
            hints: false
        }
    },
    // options...
    devServer: {
        disableHostCheck: true,
        port: 5001,
        public: "0.0.0.0:5001",
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "X-Requested-With, content-type, Authorization"
        },
        proxy: { //设置代理
            "/dev_api": {
                target: "http://localhost:5001",
                pathRewrite: { "^/dev_api": "" },
                changeOrigin: true
            },
            "/dev_api": {
                target: "http://192.168.194.241:5001",
                pathRewrite: { "^/dev_api": "" },
                changeOrigin: true
            }
        }
    }
};