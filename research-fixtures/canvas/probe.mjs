// Local fixture only. No Discord, server authorization or production claims.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
const root=process.cwd();
const server=http.createServer(async(req,res)=>{try{
 const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
 const file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
 if(!file.startsWith(root+path.sep))throw Error('outside fixture');
 const data=await readFile(file);
 res.writeHead(200,{'content-type':file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.html')?'text/html':'application/octet-stream'});res.end(data);
}catch{res.writeHead(404);res.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try {
 browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,chromiumSandbox:true});
 const page=await browser.newPage({viewport:{width:1200,height:800}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const blockedRequests=[];
 await page.route('**/*',route=>{if(new URL(route.request().url()).hostname==='127.0.0.1')return route.continue();blockedRequests.push(route.request().url());return route.abort();});
 await page.goto(`http://127.0.0.1:${server.address().port}`);
 await page.waitForFunction(()=>window.editor && !window.editor.getAppState().isLoading);
 const frame=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 await frame();
 await page.evaluate(()=>{window.events.length=0;window.editor.updateScene({elements:window.makeElements([{id:'remote-baseline',type:'rectangle',x:500,y:300,width:100,height:100}]),captureUpdate:window.capture.NEVER});});
 await page.waitForFunction(()=>window.editor.getSceneElements().some(x=>x.id==='remote-baseline'));
 await frame();
 const remoteCallbacks=await page.evaluate(()=>window.events.length);
 // This observation does not assert that callbacks are local intent or authenticated writes.
 await page.evaluate(()=>window.editor.updateScene({elements:[...window.editor.getSceneElements(),...window.makeElements([{id:'local-history',type:'ellipse',x:700,y:300,width:100,height:100}])],captureUpdate:window.capture.IMMEDIATELY}));
 await page.waitForFunction(()=>window.editor.getSceneElements().length===2);
 await page.locator('.excalidraw').click({position:{x:1000,y:650}});
 await page.keyboard.press('Control+z');
 await page.waitForFunction(()=>window.editor.getSceneElements().length===1);
 assert.deepEqual(await page.evaluate(()=>window.editor.getSceneElements().map(x=>x.id)),['remote-baseline']);
 await page.evaluate(()=>window.setReadonly(true));
 await page.waitForFunction(()=>window.editor.getAppState().viewModeEnabled===true);
 const before=await page.evaluate(()=>JSON.stringify(window.editor.getSceneElements()));
 await page.keyboard.press('r');await page.mouse.move(800,500);await page.mouse.down();await page.mouse.move(900,600,{steps:5});await page.mouse.up();
 // No selection or remaining local undo history: these are shortcut smoke attempts only.
 await page.keyboard.press('Delete');await page.keyboard.press('Control+z');await frame();
 assert.equal(await page.evaluate(()=>JSON.stringify(window.editor.getSceneElements())),before);
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({result:'local-fixture-passed',browser:browser.version(),remoteCallbacks,checks:['remote ID preserved','NEVER remote baseline survives local undo','view-mode pointer/unselected shortcut smoke leaves content unchanged'],blockedRequests,limitations:['Not yet tested in Discord','No server permission checks','No touch/stylus or accessibility acceptance','No concurrent remote overwrite/rollback coverage','Delete and undo smoke lack selection/history preconditions']},null,2));
} finally {await browser?.close();await new Promise(r=>server.close(r));}
