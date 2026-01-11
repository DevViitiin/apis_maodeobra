from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# 🔐 CONFIGURAÇÕES DO EMAIL
EMAIL_REMETENTE = "suportemaodeobra@gmail.com"
SENHA_APP = "cfuz ireu qzwo zrsi"

def enviar_email(destino, codigo):
    msg = EmailMessage()
    msg["Subject"] = "Seu código de verificação"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = destino


    msg.set_content(f"""
      <html>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f5f5f5;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 20px;">
            <tr>
              <td align="center">
                <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 500px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                  
                  <!-- Header -->
                  <tr>
                    <td style="padding: 32px 32px 24px; text-align: center; border-bottom: 1px solid #e5e5e5;">
                      <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #1a1a1a;">
                        MãoDeObra
                      </h1>
                    </td>
                  </tr>
                  
                  <!-- Body -->
                  <tr>
                    <td style="padding: 32px;">
                      <p style="margin: 0 0 24px; font-size: 16px; color: #4a4a4a; line-height: 1.5;">
                        Olá 👋
                      </p>
                      
                      <p style="margin: 0 0 24px; font-size: 16px; color: #4a4a4a; line-height: 1.5;">
                        Use o código abaixo para verificar sua conta:
                      </p>
                      
                      <div style="text-align: center; margin: 32px 0;">
                        <div style="
                          display: inline-block;
                          font-size: 32px;
                          font-weight: 700;
                          color: #1a1a1a;
                          background-color: #f8f8f8;
                          padding: 20px 40px;
                          border-radius: 8px;
                          letter-spacing: 8px;
                          border: 2px solid #e5e5e5;">
                          {codigo}
                        </div>
                      </div>
                      
                      <p style="margin: 24px 0 0; font-size: 14px; color: #737373; line-height: 1.5;">
                        Este código é válido por <strong>10 minutos</strong>.
                      </p>
                      
                      <p style="margin: 8px 0 0; font-size: 14px; color: #737373; line-height: 1.5;">
                        Se você não solicitou este código, ignore este email.
                      </p>
                    </td>
                  </tr>
                  
                  <!-- Footer -->
                  <tr>
                    <td style="padding: 24px 32px; background-color: #fafafa; border-top: 1px solid #e5e5e5; text-align: center;">
                      <p style="margin: 0; font-size: 13px; color: #999999;">
                        © 2026 MãoDeObra. Todos os direitos reservados.
                      </p>
                    </td>
                  </tr>
                  
                </table>
              </td>
            </tr>
          </table>
        </body>
      </html>
      """, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_REMETENTE, SENHA_APP)
        smtp.send_message(msg)


@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.json

    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({
            "success": False,
            "message": "Email e código são obrigatórios"
        }), 400

    try:
        enviar_email(email, code)
        return jsonify({
            "success": True,
            "message": "Código enviado com sucesso"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
