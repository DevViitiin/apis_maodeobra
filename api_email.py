from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")

def enviar_email(destinatario, codigo):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario
    msg["Subject"] = "Código de verificação - Mão de Obra"

    corpo = f"""
    <h2>Confirmação de Email</h2>
    <p>Seu código de verificação é:</p>
    <h1>{codigo}</h1>
    <p>Se você não solicitou, ignore este email.</p>
    """

    msg.attach(MIMEText(corpo, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json

    email = data.get("email")
    codigo = data.get("codigo")

    if not email or not codigo:
        return jsonify({"error": "email e codigo são obrigatórios"}), 400

    try:
        enviar_email(email, codigo)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
