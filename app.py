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


def enviar_email(destinatario, codigo, tentativas=3):
    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        raise ValueError("Credenciais de email não configuradas no Render")

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario
    msg["Subject"] = "Código de verificação - Mão de Obra"

    corpo_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: Arial, sans-serif;">
        <h2>Confirmação de Email</h2>
        <p>Seu código de verificação é:</p>
        <h1 style="color: #4CAF50;">{codigo}</h1>
        <p>Este código expira em <strong>10 minutos</strong>.</p>
        <p>Se você não solicitou este email, ignore.</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    for tentativa in range(tentativas):
        try:
            context = ssl.create_default_context()

            with smtplib.SMTP("smtp.gmail.com", 587, timeout=60) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(EMAIL_REMETENTE, EMAIL_SENHA)
                server.send_message(msg)

            print(f"✅ Email enviado para {destinatario}")
            return True

        except smtplib.SMTPAuthenticationError:
            raise Exception("❌ Erro de autenticação — use SENHA DE APP do Gmail")

        except (socket.timeout, socket.error, OSError) as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")
            if tentativa == tentativas - 1:
                raise Exception("Falha ao conectar ao servidor SMTP")
            sleep(2)

@app.route("/home", methods=["GET"])
def home():
    return jsonify({'Deu certo': True}), 200

@app.route("/send-email", methods=["POST"])
def send_email():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type deve ser application/json"
        }), 415

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