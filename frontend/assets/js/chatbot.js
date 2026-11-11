(function () {
  'use strict';

  // Knowledge base: each entry has keywords + the translation key for the answer
  const KNOWLEDGE_BASE = [
    { keywords: ['how to use', 'how do i use', 'use the app', 'getting started', 'usage'], key: 'faq_how_to_use' },
    { keywords: ['predict', 'prediction', 'how to predict', 'analyse', 'analyze', 'पूर्वानुमान'], key: 'faq_how_to_predict' },
    { keywords: ['login', 'log in', 'sign in', 'signin', 'कैसे लॉगिन', 'लॉगिन कैसे'], key: 'faq_how_to_login' },
    { keywords: ['guide', 'user guide', 'manual', 'help', 'गाइड', 'यूज़र गाइड', 'मैन्युअल', 'सहायता'], key: 'faq_user_guide' },
    { keywords: ['register', 'sign up', 'create account', 'पंजीकरण', 'खाता बनाना'], key: 'faq_how_to_register' },
    { keywords: ['pdf', 'download', 'डाउनलोड', 'रिपोर्ट'], key: 'faq_how_to_download_pdf' },
    { keywords: ['history', 'past', 'previous', 'इतिहास'], key: 'faq_how_to_history' },
  ];

  function findAnswer(userText) {
    const input = userText.toLowerCase().trim();
    if (!input) return null;
    for (const entry of KNOWLEDGE_BASE) {
      for (const kw of entry.keywords) {
        if (input.includes(kw)) return entry.key;
      }
    }
    return null;
  }

  function addBotMessage(container, text) {
    const div = document.createElement('div');
    div.className = 'chat-msg bot';
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

    function addUserMessage(container, text) {
    const div = document.createElement('div');
    div.className = 'chat-msg user';
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function showTyping(container, callback) {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-msg bot';
    typingDiv.textContent = t('chatbot_typing') || 'Typing...';
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
    setTimeout(() => {
      container.removeChild(typingDiv);
      callback();
    }, 800);
  }

  function sendChatMessage() {
    const input = document.getElementById('chatbotInput');
    const messages = document.querySelector('#chatbotMessages');
    const text = input.value.trim();
    if (!text) return;
    addUserMessage(messages, text);
    input.value = '';
    const answerKey = findAnswer(text);
    showTyping(messages, () => {
      if (answerKey) {
        addBotMessage(messages, t(answerKey));
      } else {
        addBotMessage(messages, t('chatbot_no_match'));
      }
    });
  }

    function closeChatbot() {
    const panel = document.getElementById('chatbotPanel');
    const toggle = document.getElementById('chatbotToggle');
    if (panel) panel.classList.remove('show');
    if (toggle) toggle.style.display = 'flex';
  }

  function makeDraggable(handle, container) {
    if (!handle || !container) return;
    let isDown = false, offsetX = 0, offsetY = 0;
    handle.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      isDown = true;
      container.classList.add('dragging');
      const rect = container.getBoundingClientRect();
      offsetX = e.clientX - rect.left;
      offsetY = e.clientY - rect.top;
      e.preventDefault();
    });
    document.addEventListener('mouseup', () => {
      isDown = false;
      container.classList.remove('dragging');
    });
        document.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      const newX = e.clientX - offsetX;
      const newY = e.clientY - offsetY;
      const maxX = window.innerWidth - container.offsetWidth - 10;
      const maxY = window.innerHeight - container.offsetHeight - 10;
      const newLX = Math.max(10, Math.min(newX, maxX));
      const newLY = Math.max(10, Math.min(newY, maxY));
      container.style.left = newLX + 'px';
      container.style.top = newLY + 'px';
      container.style.right = 'auto';
      container.style.bottom = 'auto';
    });
  }

  function createChatbot() {
    const style = document.createElement('style');
    style.textContent = `
      #chatbotToggle { position: fixed; bottom: 24px; right: 24px; z-index: 900; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, var(--p1), var(--p2)); border: none; box-shadow: 0 6px 24px rgba(0,245,160,0.35); color: #060b14; font-size: 26px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; }
      #chatbotToggle:hover { transform: scale(1.08); box-shadow: 0 8px 32px rgba(0,245,160,0.5); }
      #chatbotToggle.dragging { cursor: grabbing; }
      #chatbotPanel { position: fixed; bottom: 100px; right: 24px; z-index: 900; width: 340px; max-width: calc(100vw - 48px); max-height: 85vh; background: var(--card); border: 1px solid var(--border); border-radius: 18px; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); box-shadow: 0 30px 80px rgba(0,0,0,0.5); display: none; flex-direction: column; overflow: hidden; }
      #chatbotPanel.show { display: flex; }
      #chatbotHeader { background: linear-gradient(135deg, var(--p1), var(--p2)); color: #060b14; font-weight: 700; font-size: 0.95rem; padding: 0.8rem 1rem; display: flex; align-items: center; justify-content: space-between; cursor: move; }
      #chatbotHeader .chat-close { background: none; border: none; color: #060b14; font-size: 1.3rem; cursor: pointer; opacity: 0.7; }
      #chatbotHeader .chat-close:hover { opacity: 1; }
      #chatbotMessages { flex: 1; overflow-y: auto; padding: 1rem; font-size: 0.85rem; line-height: 1.5; display: flex; flex-direction: column; gap: 0.6rem; }
      .chat-msg { max-width: 80%; padding: 0.55rem 0.85rem; border-radius: 12px; word-wrap: break-word; white-space: pre-wrap; }
      .chat-msg.bot { background: rgba(0,245,160,0.1); border: 1px solid rgba(0,245,160,0.2); color: var(--text); align-self: flex-start; border-bottom-left: 4px; }
      .chat-msg.user { background: rgba(0,217,245,0.12); border: 1px solid rgba(0,217,245,0.25); color: var(--text); align-self: flex-end; border-bottom-right: 4px; }
      #chatbotInputRow { display: flex; gap: 0.5rem; padding: 0.6rem; border-top: 1px solid var(--border); background: rgba(255,255,255,0.03); }
      #chatbotInputRow input { flex: 1; background: rgba(255,255,255,0.06); border: 1px solid var(--border); border-radius: 10px; color: var(--text); padding: 0.5rem 0.8rem; font-size: 0.85rem; outline: none; }
      #chatbotInputRow input::placeholder { color: var(--muted); }
      #chatbotSend { background: var(--p1); color: #060b14; border: none; border-radius: 10px; padding: 0.5rem 1rem; font-weight: 600; cursor: pointer; font-size: 0.85rem; transition: opacity 0.2s; }
      #chatbotSend:hover { opacity: 0.85; }
      #chatbotSend:disabled { opacity: 0.4; cursor: not-allowed; }
    `;
        document.head.appendChild(style);

    const toggle = document.createElement('button');
    toggle.id = 'chatbotToggle';
    toggle.innerHTML = '💬';
    toggle.title = t('chatbot_title');
    document.body.appendChild(toggle);

    const panel = document.createElement('div');
    panel.id = 'chatbotPanel';
    panel.innerHTML =
      '<div id="chatbotHeader"><span class="drag-handle">' + t('chatbot_title') +
      '</span><span class="chat-close" onclick="closeChatbot()">✕</span></div>' +
      '<div id="chatbotMessages"></div>' +
      '<div id="chatbotInputRow">' +
        '<input type="text" id="chatbotInput" placeholder="' + t('chatbot_placeholder') + '" autocomplete="off" />' +
        '<button id="chatbotSend" onclick="sendChatMessage()">' + t('chatbot_send') + '</button>' +
      '</div>';
    document.body.appendChild(panel);

    const messages = panel.querySelector('#chatbotMessages');
    addBotMessage(messages, t('chatbot_welcome'));

    toggle.addEventListener('click', () => {
      panel.classList.add('show');
      toggle.style.display = 'none';
    });

    const inputEl = panel.querySelector('#chatbotInput');
    inputEl.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); sendChatMessage(); }
    });

    makeDraggable(panel.querySelector('#chatbotHeader'), panel);
    makeDraggable(toggle);
  }

  // Expose globals for inline onclick handlers
  window.sendChatMessage = sendChatMessage;
  window.closeChatbot = closeChatbot;

  // Initialise on DOM ready
  document.addEventListener('DOMContentLoaded', createChatbot);
})();

