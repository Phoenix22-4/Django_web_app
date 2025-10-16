// Simple chat widget script
(function(){
  const fab = document.getElementById('fab-chat');
  const win = document.getElementById('chat-window');
  const closeBtn = document.getElementById('chat-close-x');
  const body = document.getElementById('chat-body');
  const input = document.getElementById('chat-text');
  const send = document.getElementById('chat-send');
  const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');

  function appendMsg(role, text){
    const div = document.createElement('div');
    div.className = 'bubble ' + role;
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function getCsrf(){
    if (csrfEl && csrfEl.value) return csrfEl.value;
    const name='csrftoken='; const parts=document.cookie.split(';');
    for (let p of parts){ p=p.trim(); if (p.startsWith(name)) return p.substring(name.length); }
    return '';
  }

  async function sendMsg(){
    const msg = input.value.trim();
    if (!msg) return;
    appendMsg('user', msg);
    input.value = '';
    try {
      const resp = await fetch('/api/ai_chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
        body: JSON.stringify({ message: msg })
      });
      const data = await resp.json();
      appendMsg('bot', data.reply || 'No response');
    } catch (e) {
      appendMsg('bot', 'Network error. Please try again.');
    }
  }

  if (fab) fab.addEventListener('click', ()=>{ win.style.display = 'block'; });
  if (closeBtn) closeBtn.addEventListener('click', ()=>{ win.style.display = 'none'; });
  if (send) send.addEventListener('click', sendMsg);
  if (input) input.addEventListener('keydown', (e)=>{ if (e.key==='Enter') sendMsg(); });
})();

