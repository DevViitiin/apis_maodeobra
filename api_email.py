import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import socket
from time import sleep

EMAIL_REMETENTE = os.environ.get('EMAIL_REMETENTE')
EMAIL_SENHA = os.environ.get('EMAIL_SENHA')

def enviar_email(destinatario, codigo, tentativas=3):
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
