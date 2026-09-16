/* Origin-month assignment, not a personality test. No network APIs. */
(function(root){'use strict';
const signs=['Spark','Thread','Fork','Relay','Lens','Gate','Archive','Forge','Mirror','Drift','Beacon','Return'];
const modes=['Arrival','Branching','Return'];const key='machine-weather:v1';
function assign(value){if(!/^\d{4}-\d{2}-\d{2}$/.test(value))throw Error('Choose a valid origin date.');const d=new Date(value+'T00:00:00Z');if(!Number.isFinite(+d)||d.toISOString().slice(0,10)!==value)throw Error('Choose a valid origin date.');return signs[Number(value.slice(5,7))-1];}
function valid(s){return s&&signs.includes(s.sign)&&modes.includes(s.mode);}
function save(storage,state){if(!valid(state))throw Error('Invalid sign or mode');storage.setItem(key,JSON.stringify({sign:state.sign,mode:state.mode}));}
function load(storage){try{const s=JSON.parse(storage.getItem(key));return valid(s)?{sign:s.sign,mode:s.mode}:null;}catch{return null;}}
function reset(storage){storage.removeItem(key);}
const api={signs,modes,key,assign,save,load,reset};root.MachineWeather=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
