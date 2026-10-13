'use strict';
const $ = id => document.getElementById(id);
let token = location.hash.slice(1) || sessionStorage.getItem('room-token') || '';
if (token) sessionStorage.setItem('room-token', token);
history.replaceState(null, '', location.pathname);
let state = {rooms: {}, projects: [], drivers: []}, active = null, modalSubmit = null;
const node = (tag, value, cls) => { const e = document.createElement(tag); if (value != null) e.textContent = value; if (cls) e.className = cls; return e; };
const error = e => { $('error').textContent = e.message || String(e); $('error').hidden = false; };
async function api(path, data) {
  const response = await fetch(path, {method: data ? 'POST' : 'GET', headers: {'X-Room-Token': token, ...(data ? {'Content-Type': 'application/json'} : {})}, ...(data ? {body: JSON.stringify(data)} : {})});
  if (!response.ok) { const value = await response.json(); throw new Error(value.error || '연결 실패'); }
  return response.json();
}
async function act(action, data = {}) { const result = await api('/api/action', {action, room_id: active, ...data}); $('error').hidden = true; await refresh(); return result; }
const current = () => state.rooms[active];
const memberName = (room, id) => id === 'owner' ? '사람' : room.members[id]?.name || id;
function options(select, choices, selected) { select.replaceChildren(); for (const [value, label] of choices) { const o = node('option', label); o.value = value; o.selected = Array.isArray(selected) ? selected.includes(value) : value === selected; select.append(o); } }
function button(label, handler) { const b = node('button', label); b.type = 'button'; b.onclick = () => Promise.resolve().then(handler).catch(error); return b; }
function card(title, detail) { const c = node('div', null, 'card'); c.append(node('strong', title)); if (detail) c.append(node('small', detail)); return c; }
async function refresh() {
  state = await api('/api/state');
  $('connection').textContent = '● 로컬 연결';
  if (!active || !state.rooms[active]) active = Object.keys(state.rooms)[0] || null;
  render();
}
function render() {
  const scroll = $('messages').scrollTop;
  $('room-list').replaceChildren();
  for (const room of Object.values(state.rooms).reverse()) {
    const b = node('button', null, 'room-item' + (active === room.id ? ' selected' : ''));
    b.append(node('strong', room.title), node('small', `${room.closed ? '종료' : '열림'} · ${Object.values(room.members).filter(m => m.active).length}명`));
    b.onclick = () => { active = room.id; $('search').value = ''; render(); }; $('room-list').append(b);
  }
  const room = current(); $('empty').hidden = !!room; $('room-content').hidden = !room; $('details').hidden = !room;
  if (!room) return;
  $('room-title').textContent = room.title; $('room-goal').textContent = room.goal;
  $('room-meta').textContent = `${room.id} · ${room.initiative || '독립 작업'} · ${room.closed ? '종료' : '열림'}`;
  $('budget').textContent = `${room.paused ? '⏸ 중단' : '● 진행'} · tx ${room.tx_count}/10 · 수신 멤버별 최대 5`;
  $('stamp').textContent = state.stamp;
  const memberChoices = Object.values(room.members).filter(m => m.active).map(m => [m.id, `${m.name} · ${m.project || m.role}`]);
  const sender = $('sender').value; const targets = [...$('targets').selectedOptions].map(o => o.value);
  options($('sender'), [['owner', '사람'], ...memberChoices], sender || 'owner'); options($('targets'), memberChoices, targets);
  for (const id of ['message','sender','targets','add-member','add-note','request-run','close-room']) $(id).disabled = room.closed;
  $('message-form').querySelector('button[type="submit"]').disabled = room.closed;
  const query = $('search').value.toLowerCase();
  $('messages').replaceChildren();
  for (const m of room.messages.filter(m => m.text.toLowerCase().includes(query))) {
    const b = node('div', null, 'bubble' + (m.sender === 'owner' ? ' owner' : ''));
    b.append(node('strong', `${memberName(room,m.sender)} → ${m.targets.map(id=>memberName(room,id)).join(', ') || '표시만'}`), node('small', `${m.at} · ${m.tx_count}/10`), node('div', m.text, 'body')); $('messages').append(b);
  }
  $('members').replaceChildren();
  for (const m of Object.values(room.members)) {
    const c = card(m.name, `${m.project || '미배정'} · ${m.role} · ${m.active ? '입장' : '퇴장'}`);
    c.append(node('span', `${m.received}/5 수신`, 'tag'), node('small', m.id));
    if (m.active && !room.closed) c.append(button('퇴장 · 인수인계', () => modal('멤버 퇴장', [{name:'summary', label:'도달점 · 남은 일 · 근거', type:'textarea'}], values => act('leave', {member_id:m.id,...values}))));
    $('members').append(c);
  }
  $('jobs').replaceChildren();
  for (const j of Object.values(room.jobs).reverse()) {
    const labels = {pending:'승인 대기', running:'실행 중', finished:'호출 종료', failed:'실행 실패', rejected:'거절', interrupted:'중단', timed_out:'시간 초과'};
    const c = card(`${memberName(room,j.member_id)} · ${labels[j.status] || j.status}`, `${j.driver} · ${j.project}`);
    c.append(node('p', j.prompt));
    if (j.status === 'pending' && !room.closed) {
      const actions = node('div', null, 'actions');
      actions.append(button('실행 내용 확인 · 승인', async () => {
        const d = await api('/api/approval-details', {room_id:active,job_id:j.id});
        modal('이 실행 승인', [{name:'details', label:'호출할 명령 · 위치 · 제한 시간', type:'pre', value:JSON.stringify(d,null,2)}, {name:'check',label:'설정한 실행기의 권한·경계를 확인하고 이 요청 실행을 승인합니다.',type:'checkbox'}], async values => { if (values.check !== true) throw new Error('실행 승인 확인이 필요합니다.'); await act('approve',{job_id:j.id}); }, '승인하고 실행');
      }), button('거절', () => act('reject',{job_id:j.id}))); c.append(actions);
    }
    if (j.status === 'running') c.append(button('중지', () => act('cancel',{job_id:j.id})));
    if (j.output) { const d = node('details'); d.append(node('summary', `실행 출력 · exit ${j.exit_code ?? '-'} · 최대 ${j.output_limit_bytes || 64000} bytes`), node('pre',j.output)); c.append(d); }
    $('jobs').append(c);
  }
  $('notes').replaceChildren();
  for (const n of room.notes.filter(n => (n.title+' '+n.text).toLowerCase().includes(query)).reverse()) { const c = card(n.title, `${memberName(room,n.author)} · ${n.at}`); c.append(node('p',n.text)); $('notes').append(c); }
  $('events').replaceChildren(); for (const e of room.events.slice(-30).reverse()) { $('events').append(node('p', `${e.at} · ${e.text}`)); }
  $('messages').scrollTop = scroll;
}
function modal(title, fields, submit, label='저장') {
  modalSubmit = submit; $('dialog-title').textContent = title; $('dialog-fields').replaceChildren();
  for (const f of fields) {
    const l = node('label',f.label); let e;
    if (f.type === 'pre') e = node('pre',f.value);
    else if (f.type === 'select') { e = node('select'); options(e,f.choices,f.value); }
    else if (f.type === 'textarea') e = node('textarea');
    else { e = node('input'); e.type = f.type || 'text'; }
    e.name = f.name;
    if (f.type !== 'pre') { e.required = !f.optional; if (f.type !== 'select') e.value = f.value || ''; if (f.type === 'textarea') e.maxLength = 24000; }
    l.append(e); $('dialog-fields').append(l);
  }
  $('dialog-form').querySelector('button[type="submit"]').textContent = label; $('dialog').showModal();
}
$('dismiss').onclick = () => $('dialog').close();
$('dialog-form').onsubmit = async event => { event.preventDefault(); const values = {}; for (const el of $('dialog-fields').querySelectorAll('input,select,textarea')) values[el.name] = el.type === 'checkbox' ? el.checked : el.value; const submit = $('dialog-form').querySelector('button[type="submit"]'); submit.disabled = true; try { await modalSubmit(values); $('dialog').close(); } catch(e) { error(e); } finally { submit.disabled = false; } };
$('new-room').onclick = () => modal('새 작업 방', [{name:'title', label:'작업 이름'},{name:'goal', label:'목표와 완료 조건', type:'textarea'},{name:'initiative',label:'공동 이니셔티브 ID (선택)',optional:true}], async values => { const r = await act('create_room', values); active = r.room_id; render(); });
$('add-member').onclick = () => modal('레포 담당 연결', [{name:'name',label:'표시 이름'},{name:'role',label:'책임',type:'select',choices:[['worker','작업 담당'],['coordinator','조정 담당'],['reviewer','리뷰 담당'],['observer','관찰']]},{name:'project',label:'실행 프로젝트',type:'select',optional:true,choices:[['','미배정'],...state.projects.map(p=>[p,p])]}], values => act('add_member',values));
$('add-note').onclick = () => modal('인수인계 노트', [{name:'title',label:'노트 제목'},{name:'text',label:'현재 판단 · 완료 증거 · 남은 일 · 재개 지점',type:'textarea'}], values => act('note',values));
$('request-run').onclick = () => {
  const members = Object.values(current().members).filter(m=>m.active && m.project && m.role !== 'observer');
  if (!state.drivers.length || !members.length) { error(new Error('로컬 설정에 projects·drivers를 등록하고 프로젝트에 멤버를 연결하세요. room/README.md에 설정 형식이 있습니다.')); return; }
  modal('에이전트 실행 요청', [{name:'member_id',label:'담당',type:'select',choices:members.map(m=>[m.id,m.name])},{name:'driver',label:'로컬 실행기',type:'select',choices:state.drivers.map(d=>[d,d])},{name:'prompt',label:'이번 실행 목표 · 허용 변경 · 검증 방법',type:'textarea'}], values=>act('request_run',values));
};
$('close-room').onclick = () => modal('작업 방 종료', [{name:'summary',label:'도달점 · 남은 작업 정본 · 미검증 범위',type:'textarea'}],values=>act('close',values));
$('message-form').onsubmit = async e => { e.preventDefault(); try { await act('message',{sender:$('sender').value,targets:[...$('targets').selectedOptions].map(o=>o.value),text:$('message').value}); $('message').value=''; $('messages').scrollTop=$('messages').scrollHeight; } catch(e) { error(e); } };
$('search').oninput = render;
$('export').onclick = async () => { try { const response = await fetch('/api/export?room_id='+encodeURIComponent(active),{headers:{'X-Room-Token':token}}); if(!response.ok) throw new Error('내보내기 실패'); const url=URL.createObjectURL(await response.blob()); const a=node('a'); a.href=url; a.download=active+'-transcript.md'; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000); } catch(e) { error(e); } };
if (!token) { $('workspace').hidden=true; $('locked').hidden=false; $('connection').textContent='토큰 필요'; }
else { refresh().catch(error); setInterval(()=>{ if (!$('dialog').open) refresh().catch(e=>{ $('connection').textContent='연결 끊김'; error(e); }); },2500); }
