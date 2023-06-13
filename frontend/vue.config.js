const { defineConfig } = require('@vue/cli-service')
const path = require('path')

function resolve(dir){
  return path.join(__dirname,dir);
}


module.exports = defineConfig({
  transpileDependencies: true,

  publicPath:'/',

      // 解析别名处理
      chainWebpack:config=>{
        config.resolve.alias.set('@c',resolve('src/components'))
    },

    // 前后端分离调用代理设置
    devServer:{
        proxy:{
            '/api':{
                target:'http://localhost:8080',	
                //ws:true,  		//proxy websockets
                changeOrigin:true,	// 如果接口跨域，需要进行这个参数配置
                pathRewrite:{"^/api":""}
            }
        }
    }
})
