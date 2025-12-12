import os
import stripe
from flask import Flask, jsonify, Response
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# ✅ Ключ только из Environment
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

def get_today_range_utc():
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())

def count_all_customers():
    total = 0
    starting_after = None
    while True:
        params = {"limit": 100}
        if starting_after:
            params["starting_after"] = starting_after

        res = stripe.Customer.list(**params)
        total += len(res.data)

        if not res.has_more:
            break
        starting_after = res.data[-1].id
    return total

def count_today_customers():
    start_ts, _ = get_today_range_utc()
    count = 0
    starting_after = None
    while True:
        params = {"limit": 100, "created": {"gte": start_ts}}
        if starting_after:
            params["starting_after"] = starting_after

        res = stripe.Customer.list(**params)
        count += len(res.data)

        if not res.has_more:
            break
        starting_after = res.data[-1].id
    return count

@app.route("/stats")
def stats():
    try:
        total = count_all_customers()
        today = count_today_customers()
        return jsonify({"total": total, "today": today})
    except Exception as e:
        return jsonify({"error": "stripe_error", "message": str(e)}), 500

@app.route("/")
def index():
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Customers Counter</title>
<style>
body { margin:0; background:black; color:white; font-family:Arial; text-align:center; }
.label { font-size:40px; margin-top:60px; opacity:0.85; }
.value { font-size:120px; margin-top:20px; font-weight:800; }
</style>
</head>
<body>

<div class="label">Customers Today</div>
<div class="value" id="today">-</div>

<div class="label" style="margin-top:80px;">Total Customers</div>
<div class="value" id="total">-</div>

<script>
async function loadStats(){
  try{
    const r = await fetch('/stats', { cache: 'no-cache' });
    const d = await r.json();
    if(d.error){
      document.getElementById('today').textContent = 'ERR';
      document.getElementById('total').textContent = 'ERR';
      return;
    }
    document.getElementById('today').textContent = d.today;
    document.getElementById('total').textContent = d.total;
  }catch(e){
    document.getElementById('today').textContent = 'ERR';
    document.getElementById('total').textContent = 'ERR';
  }
}
loadStats();
setInterval(loadStats, 15000); // каждые 15 сек
</script>

</body>
</html>
"""
    return Response(html, mimetype="text/html")
