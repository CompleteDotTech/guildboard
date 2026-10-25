import React from 'react';
import {preserveElementIds} from './preserve-ids.mjs';
import {createRoot} from 'react-dom/client';
import {Excalidraw, convertToExcalidrawElements, CaptureUpdateAction} from '@excalidraw/excalidraw';
import '@excalidraw/excalidraw/index.css';
window.EXCALIDRAW_ASSET_PATH='/node_modules/@excalidraw/excalidraw/dist/prod/';
window.events=[];
window.makeElements=elements=>preserveElementIds(convertToExcalidrawElements,elements);
window.capture=CaptureUpdateAction;
function Fixture(){
 const [readonly,setReadonly]=React.useState(false);
 window.setReadonly=setReadonly;
 return <Excalidraw excalidrawAPI={api=>window.editor=api} viewModeEnabled={readonly} onChange={(elements,state,files)=>(window.events.length < 200 && window.events.push({elements:elements.map(({id,type,x,y,width,height,version,isDeleted})=>({id,type,x,y,width,height,version,isDeleted})),viewMode:state.viewModeEnabled,files:Object.keys(files)}))}/>;
}
createRoot(document.getElementById('root')).render(<Fixture/>);
