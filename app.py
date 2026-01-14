from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import socket
from time import sleep
import os

app = Flask(__name__)
CORS(app)

# Variáveis vindas direto do Render
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE")
EMAIL_SENHA = os.environ.get("EMAIL_SENHA")


import smtplib
import ssl

def enviar_email(destinatario, codigo):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario
    msg["Subject"] = "Código de verificação - Mão de Obra"

    corpo = f"""
    <h2>Confirmação de Email</h2>
    <p>Seu código:</p>
    <h1>{codigo}</h1>
    """
    msg.attach(MIMEText(corpo, "html"))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=30) as server:
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)


@app.route("/home", methods=["GET"])
def home():
    return jsonify({'Deu certo': True}), 200

@app.route("/send-email", methods=["POST"])
def send_email():

    data = request.get_json()
    email = data.get("email")
    codigo = data.get("codigo")

    if not email or not codigo:
        return jsonify({
            "error": "email e codigo são obrigatórios"
        }), 400

    if "@" not in email or "." not in email:
        return jsonify({
            "error": "Email inválido"
        }), 400

    try:
        enviar_email(email, codigo)
        return jsonify({
            "success": True,
            "message": "Email enviado com sucesso"
        }), 200

    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return jsonify({
            "error": "Falha ao enviar email",
            "details": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "email_configured": bool(EMAIL_REMETENTE and EMAIL_SENHA)
    }), 200


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "API de Envio de Email",
        "version": "1.0.0"
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("🚀 API iniciada na porta", port)
    app.run(host="0.0.0.0", port=port)
