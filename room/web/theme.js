'use strict';
(() => {
  const key='rooms-theme-v1', media=window.matchMedia('(prefers-color-scheme: dark)');
  const modes=['system','light','dark'], palettes=['forest','ocean','sand','charcoal'];
  let setting={mode:'system',palette:'forest'};
  function read(){try{const value=JSON.parse(localStorage.getItem(key)||'{}');setting={mode:modes.includes(value.mode)?value.mode:'system',palette:palettes.includes(value.palette)?value.palette:'forest'};}catch{setting={mode:'system',palette:'forest'};}}
  function apply(){
    document.documentElement.dataset.appearance=setting.mode==='system'?(media.matches?'dark':'light'):setting.mode;
    document.documentElement.dataset.palette=setting.palette;
    for(const element of document.querySelectorAll('[data-theme-mode]'))element.value=setting.mode;
    for(const element of document.querySelectorAll('[data-theme-palette]'))element.value=setting.palette;
  }
  function save(){try{localStorage.setItem(key,JSON.stringify(setting));}catch{}apply();}
  read();apply();media.addEventListener('change',apply);
  window.addEventListener('storage',event=>{if(event.key===key){read();apply();}});
  document.addEventListener('DOMContentLoaded',()=>{
    apply();
    for(const element of document.querySelectorAll('[data-theme-mode]'))element.addEventListener('change',()=>{setting.mode=modes.includes(element.value)?element.value:'system';save();});
    for(const element of document.querySelectorAll('[data-theme-palette]'))element.addEventListener('change',()=>{setting.palette=palettes.includes(element.value)?element.value:'forest';save();});
  });
})();
