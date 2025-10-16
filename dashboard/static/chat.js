// Simple chat widget script with draggable FAB
(function(){
  const fab = document.getElementById('fab-chat');
  const win = document.getElementById('chat-window');
  const closeBtn = document.getElementById('chat-close-x');
  const body = document.getElementById('chat-body');
  const input = document.getElementById('chat-text');
  const send = document.getElementById('chat-send');
  const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');

  // Draggable FAB functionality
  if (fab) {
    let isDragging = false;
    let startY = 0;
    let startTop = 0;

    fab.addEventListener('mousedown', startDrag);
    fab.addEventListener('touchstart', startDrag, { passive: false });

    function startDrag(e) {
      if (e.type === 'mousedown' && e.button !== 0) return; // Only left click
      
      isDragging = true;
      fab.classList.add('dragging');
      
      const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;
      startY = clientY;
      
      const rect = fab.getBoundingClientRect();
      startTop = rect.top;
      
      e.preventDefault();
      
      document.addEventListener('mousemove', doDrag);
      document.addEventListener('touchmove', doDrag, { passive: false });
      document.addEventListener('mouseup', stopDrag);
      document.addEventListener('touchend', stopDrag);
    }

    function doDrag(e) {
      if (!isDragging) return;
      e.preventDefault();
      
      const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;
      const deltaY = clientY - startY;
      const newBottom = window.innerHeight - (startTop + deltaY + fab.offsetHeight);
      
      // Constrain within viewport (with 10px margins)
      const maxBottom = window.innerHeight - fab.offsetHeight - 10;
      const minBottom = 10;
      const constrainedBottom = Math.max(minBottom, Math.min(maxBottom, newBottom));
      
      fab.style.bottom = constrainedBottom + 'px';
    }

    function stopDrag(e) {
      if (!isDragging) return;
      isDragging = false;
      fab.classList.remove('dragging');
      
      document.removeEventListener('mousemove', doDrag);
      document.removeEventListener('touchmove', doDrag);
      document.removeEventListener('mouseup', stopDrag);
      document.removeEventListener('touchend', stopDrag);
      
      // If didn't move much, treat as click
      const movedDistance = Math.abs((e.type === 'touchend' ? e.changedTouches[0].clientY : e.clientY) - startY);
      if (movedDistance < 5) {
        win.style.display = 'block';
      }
    }
  }

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

  if (closeBtn) closeBtn.addEventListener('click', ()=>{ win.style.display = 'none'; });
  if (send) send.addEventListener('click', sendMsg);
  if (input) input.addEventListener('keydown', (e)=>{ if (e.key==='Enter') sendMsg(); });
})();
