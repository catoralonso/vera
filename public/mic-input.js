(function() {
  const micBtn = document.getElementById('micBtn');
  const chatInput = document.getElementById('chatInput');
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let isListening = false;

  if (!micBtn) return;

  if (!SpeechRecognition) {
    micBtn.disabled = true;
    micBtn.title = 'Reconocimiento de voz no soportado';
    return;
  }

  function createRecognition() {
    const rec = new SpeechRecognition();
    rec.lang = 'es-ES';
    rec.interimResults = true;
    rec.maxAlternatives = 1;
    rec.continuous = false;

    rec.addEventListener('start', () => {
      isListening = true;
      micBtn.textContent = '●';
      micBtn.title = 'Grabando... haz clic para detener';
    });

    rec.addEventListener('result', (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join('');
      chatInput.value = transcript;
      chatInput.dispatchEvent(new Event('input'));
    });

    rec.addEventListener('end', () => {
      isListening = false;
      micBtn.textContent = '🎙';
      micBtn.title = 'Usar micrófono';
    });

    rec.addEventListener('error', () => {
      isListening = false;
      micBtn.textContent = '🎙';
      micBtn.title = 'Usar micrófono';
    });

    return rec;
  }

  function startListening() {
    if (isListening) {
      recognition?.stop();
      return;
    }
    recognition = createRecognition();
    try {
      recognition.start();
    } catch (err) {
      micBtn.textContent = '🎙';
      micBtn.title = 'Usar micrófono';
    }
  }

  micBtn.addEventListener('click', startListening);
})();