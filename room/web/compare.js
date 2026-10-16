'use strict';
window.RoomCompare = (() => {
  let context=null, file=null, entries=[], selected=null, anchor=null, selectionSide='new', dragging=false, threadRoot=null, sending=false, changeIndex=-1, generation=0;
  const fail=e=>{$('compare-error').textContent=e.message||String(e);$('compare-error').hidden=false;};
  const clearError=()=>{$('compare-error').hidden=true;};
  const askKey=()=>context&&file ? 'room-code-question-'+context.room_id+'-'+context.project+'-'+file.path : null;
  function saveQuestion(){const key=askKey();if(key)sessionStorage.setItem(key+'-chat-v1',JSON.stringify({text:$('code-question').value,selected,selectionSide,threadRoot,digest:file.digest}));}
  function restoreQuestion(){
    const raw=sessionStorage.getItem(askKey()+'-chat-v1')||'';
    let draft;try{draft=JSON.parse(raw);}catch{}
    $('code-question').value=draft&&typeof draft.text==='string'?draft.text:sessionStorage.getItem(askKey())||'';
    selected=draft?.digest===file.digest&&Array.isArray(draft?.selected)&&draft.selected.length===2&&draft.selected.every(Number.isInteger)&&draft.selected[0]>=0&&draft.selected[0]<=draft.selected[1]&&draft.selected[1]<file.rows.length?draft.selected:null;
    selectionSide=draft?.selectionSide==='old'?'old':'new';anchor=selected?.[0]??null;
    threadRoot=typeof draft?.threadRoot==='string'?draft.threadRoot:null;
  }
  const request=(path='')=>'/api/diff?'+new URLSearchParams({...context,...(path?{path}:{})});
  const editableTarget=element=>element?.matches('input,textarea,select,[contenteditable="true"]');
  function clearSelection(){selected=null;anchor=null;renderSelection();saveQuestion();}
  function renderSelection(){
    const ranges=selectionRanges();
    $('compare-selection').textContent=Object.entries(ranges).map(([side,range])=>`${side==='old'?'변경 전':'변경 후'} L${range[0]}–${range[1]}`).join(' · ')||'바뀐 줄 첨부';
    $('compare-code').querySelectorAll('tbody tr').forEach(row=>{for(const cell of row.cells)cell.classList.toggle('picked',!!selected&&cell.dataset.side===selectionSide&&+row.dataset.index>=selected[0]&&+row.dataset.index<=selected[1]);});
    const rows=file?.rows.filter((row,index)=>selected?index>=selected[0]&&index<=selected[1]:row.kind==='change')||[];
    $('code-attachment-title').textContent=file?file.path+' · 첨부 코드':'첨부 코드 없음';
    $('code-attachment-preview').textContent=rows.slice(0,12).map(row=>selected?`${selectionSide==='old'?'전':'후'} L${row[selectionSide+'_line']??'-'}  ${row[selectionSide]}`:`전 L${row.old_line??'-'}  ${row.old}\n후 L${row.new_line??'-'}  ${row.new}`).join('\n')+(rows.length>12?'\n… 미리보기 생략':'');
  }
  function selectionRanges(){
    if(!selected||!file)return {};
    const rows=file.rows.slice(selected[0],selected[1]+1), result={};
    const numbers=rows.map(row=>row[selectionSide+'_line']).filter(n=>n!==null);if(numbers.length)result[selectionSide]=[Math.min(...numbers),Math.max(...numbers)];
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
    for(const title of ['줄','변경 전','줄','변경 후'])heading.append(node('th',title));
    head.append(heading);table.append(head);const body=node('tbody');
    file.rows.forEach((row,index)=>{
      const tr=node('tr',null,row.kind);tr.dataset.index=index;if(row.change!==null)tr.dataset.change=row.change;
      for(const side of ['old','new']){
        const number=node('td',row[side+'_line']??'', 'line-number'),content=node('td',null,'source '+side);
        number.dataset.side=content.dataset.side=side;
        content.append(row.kind==='change'&&row.old_line!==null&&row.new_line!==null?marked(row[side],row[side==='old'?'new':'old']):node('code',row[side]));
        if(row[side+'_line']===null)content.classList.add('missing');tr.append(number,content);
      }
      tr.onpointerdown=event=>{
        if(event.button!==0)return;
        const side=event.target.closest('td')?.dataset.side;if(!side||row[side+'_line']===null)return;
        if(event.shiftKey&&anchor!==null&&selectionSide===side)selected=[Math.min(anchor,index),Math.max(anchor,index)];else{anchor=index;selectionSide=side;selected=[index,index];}
        dragging=true;renderSelection();saveQuestion();
      };
      tr.onpointerenter=event=>{if(dragging&&event.buttons===1&&anchor!==null){selected=[Math.min(anchor,index),Math.max(anchor,index)];renderSelection();saveQuestion();}};
      body.append(tr);
    });
    table.append(body);view.append(table);
    if(!file.rows.length)view.append(node('p','텍스트 줄 차이가 없습니다. 파일 모드 또는 개행 변경을 확인하세요.'));
    renderSelection();
  }
  const questionText=job=>job.diff_context?.question||job.prompt.replace(/^코드 비교 질문: /,'').split('\n')[0];
  const fileJobs=()=>Object.values(state.rooms[context?.room_id]?.jobs||{}).filter(job=>job.diff_context?.project===context?.project&&job.diff_context?.path===file?.path);
  const rootOf=job=>job.diff_context.thread_id||job.id;
  function chatJobs(){return threadRoot?fileJobs().filter(job=>rootOf(job)===threadRoot):[];}
  function populateQuestionChoices(){
    const room=state.rooms[context?.room_id],root=room?.jobs[threadRoot];
    options($('question-member'),Object.values(room?.members||{}).filter(m=>m.active&&m.project===context.project&&m.role!=='observer').map(m=>[m.id,m.name]),root?.member_id||$('question-member').value);
    options($('question-driver'),state.drivers.filter(id=>state.driver_modes?.[id]==='read-only').map(id=>[id,id]),root?.driver||$('question-driver').value);
    const latest=chatJobs().at(-1),waiting=latest&&['pending','running'].includes(latest.status),stale=latest&&latest.diff_context.digest!==file?.digest;
    const disabled=sending||!file||file.binary||file.unsupported||room?.closed||!$('question-member').options.length||!$('question-driver').options.length||waiting||stale;
    $('compare-question-form').querySelector('button[type=submit]').disabled=!!disabled;
    $('ask-selection').disabled=!file||file.binary||file.unsupported;
    $('code-chat-status').textContent=sending?'전송 내용을 준비하는 중…':waiting?'이 질문의 승인·응답을 기다리고 있습니다.':stale?'파일이 바뀌었습니다. 새 대화를 시작하세요.':latest?.status==='finished'?'앞선 질문·답변을 함께 전달합니다. Ctrl/Cmd+Enter로 보내기':'전송 내용을 확인하고 건별 승인 후 실행합니다.';
  }
  function restoreJobSelection(job){
    if(job.diff_context.digest!==file?.digest)return;
    const ranges=job.diff_context.selection||{},side=ranges.new?'new':'old',range=ranges[side];
    if(!range){clearSelection();return;}
    const indices=file.rows.flatMap((row,index)=>row[side+'_line']>=range[0]&&row[side+'_line']<=range[1]?[index]:[]);
    if(!indices.length)return;
    selectionSide=side;selected=[indices[0],indices.at(-1)];anchor=selected[0];renderSelection();saveQuestion();
    const target=$('compare-code').querySelector(`tr[data-index="${selected[0]}"]`);if(target)$('compare-code').scrollTop=target.offsetTop;
  }
  function update(){
    if(!$('compare').open||!context)return;
    const room=state.rooms[context.room_id],all=fileJobs(),roots=all.filter(job=>rootOf(job)===job.id);
    options($('code-chat-thread'),[['','새 대화'],...roots.map(job=>[job.id,questionText(job).slice(0,32)])],threadRoot||'');
    if(threadRoot&&!all.some(job=>rootOf(job)===threadRoot))threadRoot=null;
    populateQuestionChoices();
    const log=$('compare-answers'),nearEnd=log.scrollHeight-log.scrollTop-log.clientHeight<35,scroll=log.scrollTop;
    log.replaceChildren();
    const jobs=chatJobs();
    if(!jobs.length){const empty=node('div',null,'code-chat-empty');empty.append(node('strong','코드를 선택하고 질문하세요'),node('p','변경 전 또는 후의 줄을 클릭하거나 드래그하세요. Shift+클릭으로 여러 줄을 고를 수 있습니다.'),node('small','답변을 받은 뒤 같은 대화에서 후속 질문을 보낼 수 있습니다.'));log.append(empty);}
    const labels={pending:'전송 승인 대기',running:'AI가 답변을 준비하고 있습니다…',finished:'답변 도착',failed:'실행 실패',rejected:'전송 거절',interrupted:'실행 중단',timed_out:'시간 초과'};
    for(const job of jobs){
      const user=node('article',null,'code-chat-message human'),attachment=job.diff_context;
      user.append(node('small','나 · '+job.at),node('div',questionText(job),'code-chat-text'));
      const range=Object.entries(attachment.selection||{}).map(([side,limits])=>`${side==='old'?'전':'후'} L${limits[0]}–${limits[1]}`).join(' · ')||'바뀐 줄';
      const quote=button('↗ '+attachment.path+' · '+range,()=>restoreJobSelection(job));quote.className='code-chat-quote';quote.disabled=attachment.digest!==file?.digest;user.append(quote);log.append(user);
      const answer=node('article',null,'code-chat-message assistant');
      answer.append(node('strong','AI · '+(room.members[job.member_id]?.name||'담당')+' · '+job.driver),node('small',labels[job.status]||job.status));
      if(attachment.digest!==file?.digest)answer.append(node('small','이전 파일 지문의 대화 · 새 대화에서 질문하세요.'));
      if(attachment.history_job_ids?.length)answer.append(node('small',`이전 ${attachment.history_job_ids.length}개 문답 참고${attachment.history_truncated||attachment.older_turns_omitted?' · 일부 이력 생략':''}`));
      if(job.status==='pending'&&!room.closed)answer.append(button('전송 내용 확인 · 승인',()=>approveJob(job.id,context.room_id)),button('거절',async()=>{await api('/api/action',{action:'reject',room_id:context.room_id,job_id:job.id});await refresh();}));
      if(job.status==='running')answer.append(button('답변 중지',async()=>{await api('/api/action',{action:'cancel',room_id:context.room_id,job_id:job.id});await refresh();}));
      if(job.output)answer.append(node('div',job.output,'code-chat-text'));
      if(job.status==='finished')answer.append(node('small','업무 검증 '+(job.verification?.status||'NOT_RUN')));
      log.append(answer);
    }
    log.scrollTop=jobs.length?(nearEnd?log.scrollHeight:scroll):0;
  }
  async function loadFile(path){
    saveQuestion();const revision=++generation;file=null;selected=anchor=null;threadRoot=null;changeIndex=-1;
    $('compare-code').replaceChildren(node('p','파일을 읽는 중…'));$('compare-path').textContent=path;
    $('compare-files').querySelectorAll('button').forEach(b=>b.classList.toggle('selected',b.dataset.path===path));
    clearError();
    try{
      const result=await api(request(path));if(revision!==generation||!$('compare').open)return;
      file=result;restoreQuestion();drawFile();renderSelection();update();if(!selected)navigateChange(1);
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
  document.addEventListener('pointerup',()=>{dragging=false;});
  $('new-code-chat').onclick=()=>{threadRoot=null;saveQuestion();update();$('code-question').focus();};
  $('code-chat-thread').onchange=()=>{threadRoot=$('code-chat-thread').value||null;saveQuestion();update();};
  for(const id of ['question-member','question-driver'])$(id).onchange=()=>{threadRoot=null;saveQuestion();update();};
  $('ask-selection').onclick=()=>{$('compare-question').hidden=false;$('code-question').focus();};
  $('code-question').onkeydown=event=>{if(!event.isComposing&&event.key==='Enter'&&(event.ctrlKey||event.metaKey)){event.preventDefault();if(!$('compare-question-form').querySelector('button[type=submit]').disabled)$('compare-question-form').requestSubmit();}};
  $('compare-question-form').onsubmit=async event=>{
    event.preventDefault();if(!file||sending)return;
    const submitted=file,scope={...context},question=$('code-question').value,latest=chatJobs().at(-1),replyTo=latest?.status==='finished'?latest.id:null;
    sending=true;populateQuestionChoices();clearError();
    try{
      const accepted=await api('/api/diff/question',{...scope,path:submitted.path,digest:submitted.digest,selection:selectionRanges(),question,reply_to:replyTo,
        member_id:$('question-member').value,driver:$('question-driver').value});
      await refresh();
      if(file===submitted){threadRoot=state.rooms[scope.room_id].jobs[accepted.job_id].diff_context.thread_id;$('code-question').value='';saveQuestion();update();await approveJob(accepted.job_id,scope.room_id);}
    }catch(e){fail(e);}finally{sending=false;populateQuestionChoices();}
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
