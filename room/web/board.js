'use strict';
const $ = id => document.getElementById(id);
const node = (tag, text, cls) => { const el = document.createElement(tag); if (text != null) el.textContent = text; if (cls) el.className = cls; return el; };
const token = location.hash.slice(1) || sessionStorage.getItem('room-board-token') || '';
if (token) sessionStorage.setItem('room-board-token', token);
history.replaceState(null, '', '/board');
const labels = {running:'작업 중', approval:'승인 대기', recovery:'재개 판단 대기', paused:'예산 중단', idle:'대기', closed:'종료'};
let snapshot = null;
async function refresh() {
  try {
    const response = await fetch('/api/board', {headers:{'X-Room-Token':token}});
    if (!response.ok) throw new Error(response.status === 403 ? '오너 화면에서 새 관찰 주소를 열어주세요. 서버 재시작 후에는 새 토큰이 필요합니다.' : '서버를 확인하세요.');
    snapshot = await response.json();
    $('connection').textContent = '● 로컬 연결'; $('notice').hidden = true;
    $('totals').replaceChildren();
    for (const [key,label] of [['rooms','전체 방'],['running','실행 중'],['pending','승인 대기'],['recovery','재개 판단']]) {
      const card = node('div', null, 'total'); card.append(node('strong', snapshot.totals[key]),node('small',label)); $('totals').append(card);
    }
    $('rooms').replaceChildren();
    if (!snapshot.rooms.length) $('rooms').append(node('p','아직 열린 작업 방이 없습니다.','empty'));
    for (const room of snapshot.rooms) {
      const card = node('article',null,'room'); card.dataset.status=room.status;
      const header=node('div',null,'room-head'); header.append(node('strong',room.alias),node('span',labels[room.status] || '확인 필요','badge')); card.append(header);
      const garden=node('div',null,'garden'); garden.setAttribute('aria-hidden','true');
      for(let i=0;i<Math.min(room.members,10);i++) garden.append(node('span',null,'member'));
      card.append(garden,node('p',`연결 ${room.members} · 실행 ${room.running} · 승인 ${room.pending}`),node('p',`재개 판단 ${room.recovery} · 전달 ${room.tx_count}/${room.tx_limit}`));
      const meter=node('meter',null,'budget'); meter.min=0;meter.max=room.tx_limit;meter.value=room.tx_count;meter.setAttribute('aria-label','전달 예산');card.append(meter);
      $('rooms').append(card);
    }
    $('download').disabled=false;
  } catch(error) {
    $('connection').textContent='연결 끊김 · 현황 미확인';$('notice').textContent=error.message;$('notice').hidden=false;$('download').disabled=true;
  }
}
$('download').onclick=()=>{
  if(!snapshot)return;
  const url=URL.createObjectURL(new Blob([JSON.stringify(snapshot,null,2)],{type:'application/json'}));
  const link=node('a');link.href=url;link.download='room-observation.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
refresh();setInterval(refresh,3000);
