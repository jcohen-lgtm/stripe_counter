from flask import Flask, jsonify, Response
import stripe
from datetime import datetime, timezone, timedelta
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = Flask(__name__)

def get_today_start_utc():
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    return int(start.timestamp())

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
    start_ts = get_today_start_utc()
    count = 0
    starting_after = None

    while True:
        params = {
            "limit": 100,
            "created": {"gte": start_ts}
        }
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
        print("STRIPE ERROR:", e)
        return jsonify({"error": "stripe_error"}), 500

@app.route("/")
def index():
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Customers Counter</title>
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

<div class="label">Customers Today</div>
<div class="value" id="today">-</div>

<div class="label" style="margin-top:80px;">Total Customers</div>
<div class="value" id="total">-</div>

<script>
async function loadStats(){
  try{
    const r = await fetch('/stats');
    const d = await r.json();
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
