'use strict';
window.RoomCompare = (() => {
  let context=null, file=null, entries=[], selected=null, anchor=null, changeIndex=-1, generation=0;
  const fail=e=>{$('compare-error').textContent=e.message||String(e);$('compare-error').hidden=false;};
  const clearError=()=>{$('compare-error').hidden=true;};
  const askKey=()=>context&&file ? 'room-code-question-'+context.room_id+'-'+context.project+'-'+file.path : null;
  function saveQuestion(){const key=askKey();if(key)sessionStorage.setItem(key,$('code-question').value);}
  const request=(path='')=>'/api/diff?'+new URLSearchParams({...context,...(path?{path}:{})});
  const editableTarget=element=>element?.matches('input,textarea,select,[contenteditable="true"]');
  function clearSelection(){selected=null;anchor=null;renderSelection();}
  function renderSelection(){
    const ranges=selectionRanges();
    $('compare-selection').textContent=Object.entries(ranges).map(([side,range])=>`${side==='old'?'전':'후'} L${range[0]}–${range[1]}`).join(' · ')||'선택 없음 · 바뀐 줄 기준';
    $('compare-code').querySelectorAll('tbody tr').forEach(row=>row.classList.toggle('picked',!!selected&&+row.dataset.index>=selected[0]&&+row.dataset.index<=selected[1]));
  }
  function selectionRanges(){
    if(!selected||!file)return {};
    const rows=file.rows.slice(selected[0],selected[1]+1), result={};
    for(const side of ['old','new']){const numbers=rows.map(row=>row[side+'_line']).filter(n=>n!==null);if(numbers.length)result[side]=[Math.min(...numbers),Math.max(...numbers)];}
    return result;
  }
  function marked(value,other){
    const code=node('code');
    if(value===other){code.textContent=value;return code;}
    let start=0,end=0;
    while(start<value.length&&start<other.length&&value[start]===other[start])start++;
    while(end<value.length-start&&end<other.length-start&&value[value.length-end-1]===other[other.length-end-1])end++;
    code.append(document.createTextNode(value.slice(0,start)),node('mark',value.slice(start,value.length-end)),document.createTextNode(value.slice(value.length-end)));
    return code;
  }
  function drawFile(){
    const view=$('compare-code');view.replaceChildren();
    view.classList.toggle('changes-only',$('changed-only').checked);view.classList.toggle('no-wrap',!$('compare-wrap').checked);
    if(!file)return;
    $('compare-path').textContent=file.path+(file.newline_changed?' · 끝 개행 변경':'');
    if(file.binary||file.unsupported){view.append(node('p',file.binary?'이진 파일입니다. 내용과 질문을 제공하지 않습니다.':'symlink·submodule 등 일반 소스 파일이 아닌 항목입니다.'));return;}
    const table=node('table'), head=node('thead'), heading=node('tr');
    for(const title of ['전 줄','고치기 전','후 줄','고친 후'])heading.append(node('th',title));
    head.append(heading);table.append(head);const body=node('tbody');
    file.rows.forEach((row,index)=>{
      const tr=node('tr',null,row.kind);tr.dataset.index=index;if(row.change!==null)tr.dataset.change=row.change;
      for(const side of ['old','new']){
        const number=node('td',row[side+'_line']??'', 'line-number'),content=node('td',null,'source '+side);
        content.append(row.kind==='change'&&row.old_line!==null&&row.new_line!==null?marked(row[side],row[side==='old'?'new':'old']):node('code',row[side]));
        if(row[side+'_line']===null)content.classList.add('missing');tr.append(number,content);
      }
      tr.onclick=event=>{if(event.shiftKey&&anchor!==null)selected=[Math.min(anchor,index),Math.max(anchor,index)];else{anchor=index;selected=[index,index];}renderSelection();};
      body.append(tr);
    });
    table.append(body);view.append(table);
    if(!file.rows.length)view.append(node('p','텍스트 줄 차이가 없습니다. 파일 모드 또는 개행 변경을 확인하세요.'));
    renderSelection();
  }
  function populateQuestionChoices(){
    const room=state.rooms[context?.room_id];
    options($('question-member'),Object.values(room?.members||{}).filter(m=>m.active&&m.project===context.project&&m.role!=='observer').map(m=>[m.id,m.name]),$('question-member').value);
    options($('question-driver'),state.drivers.filter(id=>state.driver_modes?.[id]==='read-only').map(id=>[id,id]),$('question-driver').value);
    const disabled=!file||file.binary||file.unsupported||room?.closed||!$('question-member').options.length||!$('question-driver').options.length;
    $('compare-question-form').querySelector('button').disabled=!!disabled;
  }
  function update(){
    if(!$('compare').open||!context)return;
    populateQuestionChoices();
    const log=$('compare-answers'), nearEnd=log.scrollHeight-log.scrollTop-log.clientHeight<35, scroll=log.scrollTop;
    log.replaceChildren();
    const room=state.rooms[context.room_id];
    for(const job of Object.values(room?.jobs||{}).filter(j=>j.diff_context?.project===context.project&&j.diff_context?.path===file?.path).slice(-6)){
      const card=node('div',null,'code-answer');
      card.append(node('strong',job.prompt.replace(/^코드 비교 질문: /,'').split('\n')[0]),node('small',`${job.status} · 검증 ${job.verification?.status||'NOT_RUN'}`));
      if(file&&job.diff_context.digest!==file.digest)card.append(node('small','이전 파일 지문에 대한 질문입니다.'));
      if(job.status==='pending'&&!room.closed)card.append(button('자료 확인 · 승인',()=>approveJob(job.id,context.room_id)),button('거절',async()=>{await api('/api/action',{action:'reject',room_id:context.room_id,job_id:job.id});await refresh();}));
      if(job.status==='running')card.append(button('중지',async()=>{await api('/api/action',{action:'cancel',room_id:context.room_id,job_id:job.id});await refresh();}));
      if(job.output)card.append(node('pre',job.output));
      log.append(card);
    }
    log.scrollTop=nearEnd?log.scrollHeight:scroll;
  }
  async function loadFile(path){
    saveQuestion();const revision=++generation;file=null;selected=anchor=null;changeIndex=-1;
    $('compare-code').replaceChildren(node('p','파일을 읽는 중…'));$('compare-path').textContent=path;
    $('compare-files').querySelectorAll('button').forEach(b=>b.classList.toggle('selected',b.dataset.path===path));
    clearError();
    try{
      const result=await api(request(path));if(revision!==generation||!$('compare').open)return;
      file=result;$('code-question').value=sessionStorage.getItem(askKey())||'';drawFile();clearSelection();update();navigateChange(1);
    }catch(e){if(revision===generation){$('compare-code').replaceChildren(node('p','파일을 불러오지 못했습니다.'));fail(e);update();}}
  }
  async function load(){
    saveQuestion();const revision=++generation;clearError();file=null;entries=[];
    context={room_id:context.room_id,project:$('compare-project').value,comparison:$('compare-mode').value,base:$('compare-base').value.trim(),head:$('compare-head').value.trim()};
    $('compare-files').replaceChildren();$('compare-code').replaceChildren(node('p','변경 목록을 읽는 중…'));
    try{
      const result=await api(request());if(revision!==generation||!$('compare').open)return;
      context.base=result.base;context.head=result.head;entries=result.files;
      $('compare-info').textContent=`${result.base.slice(0,12)} → ${result.head==='WORKTREE'?'현재 작업 파일':result.head.slice(0,12)} · 변경 ${entries.length}개 · 인증/환경 경로 제외 ${result.excluded}개 · untracked 제외 · rename은 삭제/추가로 표시`;
      for(const item of entries){const b=button(`${item.status} ${item.path}`,()=>loadFile(item.path));b.dataset.path=item.path;b.append(node('small',item.binary?'이진 파일':`+${item.added??0} / −${item.deleted??0}`));$('compare-files').append(b);}
      if(entries.length)await loadFile(entries[0].path);
      else{$('compare-path').textContent='변경 0개';$('compare-code').replaceChildren(node('p','선택한 범위에 추적 중인 파일 변경이 없습니다.'));update();}
    }catch(e){if(revision===generation){$('compare-code').replaceChildren(node('p','비교 범위를 불러오지 못했습니다.'));fail(e);update();}}
  }
  async function open(values={}){
    const room=current();if(!room)throw new Error('작업 방을 먼저 선택하세요.');
    const projects=[...new Set(Object.values(room.members).map(m=>m.project).filter(p=>state.projects.includes(p)))];
    if(!projects.length)throw new Error('등록된 실행 프로젝트에 멤버를 먼저 연결하세요.');
    if(values.project&&!projects.includes(values.project))throw new Error('이 방에 연결된 프로젝트를 선택하세요.');
    saveQuestion();context={room_id:room.id};file=null;
    options($('compare-project'),projects.map(p=>[p,p]),values.project||projects[0]);
    $('compare-mode').value=values.head?'merge-base':'working';$('compare-base').value=values.base||'HEAD';$('compare-head').value=values.head||'HEAD';modeChanged();
    if(!$('compare').open)$('compare').showModal();await load();
  }
  function navigateFile(step){if(!entries.length)return;const index=entries.findIndex(entry=>entry.path===file?.path);const next=Math.min(entries.length-1,Math.max(0,index+step));if(next!==index)loadFile(entries[next].path);}
  function navigateChange(step){
    const changes=[...new Set((file?.rows||[]).map(row=>row.change).filter(n=>n!==null))];if(!changes.length)return;
    changeIndex=Math.max(0,Math.min(changes.length-1,changeIndex+step));
    const target=$('compare-code').querySelector(`tr[data-change="${changes[changeIndex]}"]`);
    if(target)$('compare-code').scrollTop=target.offsetTop-($('compare-code').querySelector('thead')?.offsetHeight||0);
  }
  function modeChanged(){$('compare-head').disabled=$('compare-mode').value==='working';}
  function close(){saveQuestion();generation++;$('compare').close();}
  $('open-compare').onclick=()=>open().catch(error);
  $('compare-close').onclick=close;
  $('compare').addEventListener('cancel',event=>{if(selected){event.preventDefault();clearSelection();}else{saveQuestion();generation++;}});
  $('compare').addEventListener('close',()=>{saveQuestion();generation++;});
  $('compare-form').onsubmit=event=>{event.preventDefault();load();};
  $('compare-mode').onchange=modeChanged;
  $('previous-file').onclick=()=>navigateFile(-1);$('next-file').onclick=()=>navigateFile(1);
  $('previous-change').onclick=()=>navigateChange(-1);$('next-change').onclick=()=>navigateChange(1);
  $('changed-only').onchange=drawFile;
  $('compare-wrap').onchange=()=>{sessionStorage.setItem('room-compare-wrap',String($('compare-wrap').checked));drawFile();};
  $('compare-wrap').checked=sessionStorage.getItem('room-compare-wrap')!=='false';
  $('clear-selection').onclick=clearSelection;
  $('toggle-question').onclick=()=>{$('compare-question').hidden=!$('compare-question').hidden;};
  $('code-question').oninput=saveQuestion;
  $('compare-question-form').onsubmit=async event=>{
    event.preventDefault();if(!file)return;
    const submitted=file,scope={...context},question=$('code-question').value,submit=event.submitter;
    submit.disabled=true;clearError();
    try{
      await api('/api/diff/question',{...scope,path:submitted.path,digest:submitted.digest,selection:selectionRanges(),question,
        member_id:$('question-member').value,driver:$('question-driver').value});
      await refresh();
      if(file===submitted){$('code-question').value='';saveQuestion();update();}
    }catch(e){fail(e);}finally{populateQuestionChoices();}
  };
  $('compare-code').onkeydown=event=>{
    if(event.isComposing||editableTarget(event.target)||event.ctrlKey||event.metaKey)return;
    const key=event.code;const view=$('compare-code');
    const handlers={KeyJ:()=>navigateChange(1),KeyK:()=>navigateChange(-1),KeyN:()=>navigateFile(1),KeyP:()=>navigateFile(-1),KeyW:()=>{$('compare-wrap').click();},
      ArrowDown:()=>view.scrollBy(0,24),ArrowUp:()=>view.scrollBy(0,-24),ArrowRight:()=>view.scrollBy(80,0),ArrowLeft:()=>view.scrollBy(-80,0),
      PageDown:()=>view.scrollBy(0,view.clientHeight-48),PageUp:()=>view.scrollBy(0,-view.clientHeight+48),
      Space:()=>view.scrollBy(0,(event.shiftKey?-1:1)*(view.clientHeight-48)),Home:()=>{view.scrollTop=0;},End:()=>{view.scrollTop=view.scrollHeight;}};
    if(handlers[key]){event.preventDefault();handlers[key]();}
  };
  return {open,update};
})();
