from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")


def enviar_email(destinatario, codigo):
    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        raise ValueError("Credenciais de email não configuradas")
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destinatario
    msg["Subject"] = "Código de verificação - Mão de Obra"

    corpo = f"""
    <html>
    <body>
        <h2>Confirmação de Email</h2>
        <p>Seu código de verificação é:</p>
        <h1 style="color: #4CAF50;">{codigo}</h1>
        <p>Este código expira em 10 minutos.</p>
        <p>Se você não solicitou, ignore este email.</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(corpo, "html"))

    # Mudança aqui: SMTP_SSL na porta 465
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)
        

@app.route("/send-email", methods=["POST"])
def send_email():
    # Verifica se o Content-Type é JSON
    if not request.is_json:
        return jsonify({"error": "Content-Type deve ser application/json"}), 415
    
    data = request.get_json()
    email = data.get("email")
    codigo = data.get("codigo")
    
    print(f'Email do destinatário: {email}')

    if not email or not codigo:
        return jsonify({"error": "email e codigo são obrigatórios"}), 400

    try:
        enviar_email(email, codigo)
        return jsonify({"success": True, "message": "Email enviado com sucesso"}), 200
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return jsonify({"error": "Falha ao enviar email", "details": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
