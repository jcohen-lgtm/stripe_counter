from flask import Flask, jsonify, Response
import stripe
from datetime import datetime, timezone, timedelta

# 🔐 ВСТАВЬ СЮДА СВОЙ СЕКРЕТНЫЙ КЛЮЧ STRIPE!
# Например: "sk_live_XXXX..." или "sk_test_XXXX..."
stripe.api_key = "mk_1SdOnoJNr1UL0NgJ70Bh82mt"

app = Flask(__name__)


def get_today_range_utc():
now = datetime.now(timezone.utc)
start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
end = start + timedelta(days=1)
return int(start.timestamp()), int(end.timestamp())


def count_customers(query):
# Используем Stripe Search API: customers.search
res = stripe.Customer.search(query=query, limit=1)
return res.get("total_count", 0)


@app.route("/stats")
def stats():
try:
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
<title>Stripe Counter</title>
<style>
body {
margin:0;
background:black;
color:white;
font-family:Arial;
text-align:center;
}
.label {
font-size:40px;
margin-top:60px;
opacity:0.8;
}
.value {
font-size:120px;
margin-top:20px;
font-weight:bold;
}
</style>
</head>
<body>

<div class="label">Клиентов сегодня</div>
<div class="value" id="today">-</div>

<div class="label" style="margin-top:80px;">Клиентов всего</div>
<div class="value" id="total">-</div>

<script>
async function loadStats(){
try{
let r = await fetch('/stats');
let d = await r.json();
document.getElementById('today').textContent = d.today;
document.getElementById('total').textContent = d.total;
}catch(e){
document.getElementById('today').textContent = 'ERR';
document.getElementById('total').textContent = 'ERR';
}
}
loadStats();
setInterval(loadStats, 60000);
</script>

</body>
</html>
"""
return Response(html, mimetype="text/html")


if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)