const http=require('http'),fs=require('fs'),path=require('path');
module.exports=async function fixtureServer(root){
 const types={'.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2','.json':'application/json','.html':'text/html'};
 const server=http.createServer((req,res)=>{let name=decodeURIComponent(new URL(req.url,'http://local').pathname);if(!path.extname(name))name='/index.html';const file=path.resolve(root,'.'+name);if(!file.startsWith(path.resolve(root)+path.sep)||!fs.existsSync(file)){res.writeHead(404);res.end();return}res.writeHead(200,{'content-type':types[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res)});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));return {origin:'http://127.0.0.1:'+server.address().port,close:()=>new Promise(resolve=>server.close(resolve))};
};
