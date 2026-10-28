import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// Local development only. The proxy never ships in the production bundle.
export default defineConfig({
 plugins:[react()],base:'/',
 server:{proxy:{'/avideo-local':{target:'https://localhost',changeOrigin:true,secure:false,rewrite:path=>path.replace(/^\/avideo-local/,'')}}}
});
