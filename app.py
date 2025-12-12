from flask import Flask, jsonify, Response
import stripe
from datetime import datetime, timezone, timedelta
import os

# ✅ Stripe key хранится в переменной окружения (Render -> Environment)
stripe.api_key = os.environ.get("mk_1SdOnoJNr1UL0NgJ70Bh82mt", "")

app = Flask(__name__)

def get_today_range_utc():
now = datetime.now(timezone.utc)
start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
end = start + timedelta(days=1)
return int(start.timestamp()), int(end.timestamp())

def count_customers(query: str) -> int:
res = stripe.Customer.search(query=query, limit=1)
return res.get("total_count", 0)

@app.route("/stats")
def stats():
try:
if not stripe.api_key:
return jsonify({"error": "missing_stripe_key"}), 500

total = count_customers("created>0")
start_ts, end_ts = get_today_range_utc()
today = count_customers(f"created>={start_ts} AND created<{end_ts}")

return jsonify({"total": total, "today": today})
except Exception as e:
print("ERROR:", e)
return jsonify({"error": "stripe_error"}), 500

@app.route("/")
def index():
html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Customers Counter</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { margin:0; background:#000; color:#fff; font-family: Arial, sans-serif; text-align:center; }
.label { font-size:40px; margin-top:60px; opacity:0.85; }
.value { font-size:120px; margin-top:20px; font-weight:800; }
.btn {
margin-top: 30px;
font-size: 28px;
padding: 18px 26px;
border-radius: 12px;
border: 0;
cursor: pointer;
}
.hint { margin-top: 14px; opacity: 0.75; font-size: 20px; }
</style>
</head>
<body>

<div class="label">Customers Today</div>
<div class="value" id="today">-</div>

<div class="label" style="margin-top:80px;">Total Customers</div>
<div class="value" id="total">-</div>

<button class="btn" id="soundBtn">Enable Sound</button>
<div class="hint">Tap once to allow sound. Then it will play when a new customer appears.</div>

<script>
let lastToday = null;
let soundEnabled = false;

// Создаём простой "бип" через WebAudio (без mp3 файлов)
let audioCtx = null;
function playBeep(){
if (!soundEnabled) return;
try{
if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
const o = audioCtx.createOscillator();
const g = audioCtx.createGain();
o.type = "sine";
o.frequency.value = 880; // частота
g.gain.value = 0.08; // громкость
o.connect(g);
g.connect(audioCtx.destination);
o.start();
setTimeout(()=>{ o.stop(); }, 250); // длительность
}catch(e){
console.log("Audio error:", e);
}
}

document.getElementById("soundBtn").addEventListener("click", async () => {
soundEnabled = true;
document.getElementById("soundBtn").textContent = "Sound Enabled ✅";
// "разбудим" аудио-контекст кликом
playBeep();
});

async function loadStats(){
try{
const r = await fetch('/stats', { cache: 'no-cache' });
const d = await r.json();

if (d.error) {
document.getElementById('today').textContent = 'ERR';
document.getElementById('total').textContent = 'ERR';
return;
}

document.getElementById('today').textContent = d.today;
document.getElementById('total').textContent = d.total;

// Если число "today" выросло — играем звук
if (lastToday !== null && d.today > lastToday) {
playBeep();
}
lastToday = d.today;

}catch(e){
document.getElementById('today').textContent = 'ERR';
document.getElementById('total').textContent = 'ERR';
}
}

loadStats();
setInterval(loadStats, 15000); // каждые 15 секунд (можешь поставить 60000)
</script>

</body>
</html>
"""
return Response(html, mimetype="text/html")