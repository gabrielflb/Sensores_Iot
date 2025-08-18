 const AES_KEY = "12345678901234567890123456789012"; // 32 bytes

    async function decryptPayload(encryptedB64) {
      const raw = Uint8Array.from(atob(encryptedB64), c => c.charCodeAt(0));
      const nonce = raw.slice(0, 12);
      const ciphertext = raw.slice(12);

      const key = await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(AES_KEY),
        { name: "AES-GCM" },
        false,
        ["decrypt"]
      );

      const decrypted = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: nonce },
        key,
        ciphertext
      );

      return JSON.parse(new TextDecoder().decode(decrypted));
    }

    const ws = new WebSocket("ws://localhost:8001/ws-umidade");

    ws.onopen = () => console.log("WebSocket (umidade) conectado");
    ws.onclose = () => console.log("WebSocket (umidade) desconectado");
    ws.onerror = (e) => console.error("WebSocket (umidade) erro", e);

  ws.onmessage = async (evt) => {
  try {
    const msg = JSON.parse(evt.data); 
    const encryptedB64 = msg.payload;  
    const decrypted = await decryptPayload(encryptedB64);
    console.log("Recebido do backend:", decrypted);
    if (decrypted && decrypted.sensor === "humidity") {
      pushPoint(decrypted.value);
    }
  } catch (e) {
    console.error("Erro ao descriptografar payload:", e);
  }
};


    const ctx = document.getElementById('chartHumidity').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [{ label: 'Umidade (%)', data: [], borderColor: 'blue', fill: false }] },
      options: { responsive: true, scales: { x: { display: true }, y: { beginAtZero: true } } }
    });

    function pushPoint(value) {
      const now = new Date().toLocaleTimeString();
      chart.data.labels.push(now);
      chart.data.datasets[0].data.push(value);
      if (chart.data.labels.length > 30) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
      }
      chart.update();
    }