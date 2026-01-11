from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import socket
from time import sleep
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permite requisições de outros domínios

# Configurações de email
EMAIL_REMETENTE = os.environ.get('EMAIL_REMETENTE')
EMAIL_SENHA = os.environ.get('EMAIL_SENHA')

def enviar_email(destinatario, codigo, tentativas=3):
    """
    Envia email com código de verificação
    Faz retry automático em caso de falha
    """
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
    
    # Tenta enviar com retry
    for tentativa in range(tentativas):
        try:
            # Timeout maior para servidores em nuvem
            context = ssl.create_default_context()
            
            # Tenta porta 587 primeiro (geralmente menos bloqueada)
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=60)
            server.set_debuglevel(0)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.send_message(msg)
            server.quit()
            
            print(f"Email enviado com sucesso para {destinatario}")
            return True
            
        except (socket.timeout, socket.error, OSError) as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")
            if tentativa < tentativas - 1:
                sleep(2)  # Aguarda 2 segundos antes de tentar novamente
            else:
                raise Exception(f"Falha ao conectar ao servidor SMTP após {tentativas} tentativas")
        except smtplib.SMTPAuthenticationError as e:
            print(f"Erro de autenticação: {e}")
            raise Exception("Credenciais de email inválidas")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            raise

@app.route("/send-email", methods=["POST"])
def send_email():
    """
    Endpoint para enviar email de verificação
    Espera JSON: {"email": "destinatario@example.com", "codigo": "123456"}
    """
    # Verifica se o Content-Type é JSON
    if not request.is_json:
        return jsonify({
            "error": "Content-Type deve ser application/json"
        }), 415
    
    data = request.get_json()
    email = data.get("email")
    codigo = data.get("codigo")
    
    print(f'Email do destinatário: {email}')
    
    # Validação dos campos
    if not email or not codigo:
        return jsonify({
            "error": "email e codigo são obrigatórios"
        }), 400
    
    # Validação básica de email
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
        
    except ValueError as e:
        # Erro de configuração
        return jsonify({
            "error": "Configuração do servidor de email incorreta",
            "details": str(e)
        }), 500
        
    except Exception as e:
        # Outros erros
        print(f"Erro ao enviar email: {str(e)}")
        return jsonify({
            "error": "Falha ao enviar email",
            "details": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """
    Endpoint para verificar se a API está funcionando
    """
    return jsonify({
        "status": "ok",
        "service": "Email API",
        "email_configured": bool(EMAIL_REMETENTE and EMAIL_SENHA)
    }), 200

@app.route("/", methods=["GET"])
def index():
    """
    Endpoint raiz com informações da API
    """
    return jsonify({
        "service": "API de Envio de Email",
        "version": "1.0.0",
        "endpoints": {
            "POST /send-email": "Envia email de verificação",
            "GET /health": "Verifica status da API"
        }
    }), 200

if __name__ == "__main__":
    # Verifica se as credenciais estão configuradas
    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        print("⚠️  AVISO: Variáveis de ambiente EMAIL_REMETENTE e EMAIL_SENHA não configuradas!")
        print("Configure-as no arquivo .env ou nas variáveis de ambiente do sistema")
    else:
        print(f"✅ Email configurado: {EMAIL_REMETENTE}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
