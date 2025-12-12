import os
import stripe
from flask import jsonify

@app.route("/stats")
def stats():
    try:
        key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not key:
            return jsonify({"error": "missing_key", "hint": "Set STRIPE_SECRET_KEY in Render -> Service -> Environment"}), 500

        # не показываем ключ, только длину и первые 6 символов (безопасно)
        key_info = {"len": len(key), "prefix": key[:6]}

        stripe.api_key = key

        # простой запрос к Stripe, чтобы понять: ключ валидный или нет
        acct = stripe.Account.retrieve()

        return jsonify({"ok": True, "account_id": acct["id"], "key_info": key_info})

    except Exception as e:
        return jsonify({
            "error": "stripe_error",
            "message": str(e),
            "key_info": {"len": len(os.environ.get("STRIPE_SECRET_KEY","")), "prefix": os.environ.get("STRIPE_SECRET_KEY","")[:6]}
        }), 500
