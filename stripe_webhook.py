from flask import Flask, request, jsonify
import stripe
import sqlite3
import requests

app = Flask(__name__)
stripe.api_key = "sk_test_51QUQGNALZk2185tZWDxL8VX9DF2tnbXLLTRVVTKRTEsffh9G6LJL7Wnuc0sHzzGqYMwPa79pPcyATZMZnDvs2oop00DISVKF5X"
webhook_secret = "whsec_e734bdcce3316a42cdad0b559836aabf89351b6792606fadef6eadcfcd2e66fd "

# Обработчик Webhook
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({"error": str(e)}), 400

    # Обработка события "checkout.session.completed"
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_id = session["metadata"]["telegram_id"]

        # Обновляем статус подписки в базе данных
        conn = sqlite3.connect("tenants.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tenants SET subscription_active = 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        conn.close()

        print(f"Subscription activated for Telegram ID: {telegram_id}")

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)