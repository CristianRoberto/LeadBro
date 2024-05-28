from googleapiclient.errors import HttpError
from .Google import Create_Service
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email.mime.base import MIMEBase
from email import encoders
import mimetypes

from dotenv import load_dotenv
load_dotenv()

class GMAIL:
    
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']

    def __init__(self) -> None:
        # Construye la ruta al archivo credentials.json
        CLIENT_SECRET_FILE = os.getenv("GOOGLE_CREDENTIALS")
        self.service = Create_Service(CLIENT_SECRET_FILE, self.API_NAME, self.API_VERSION, self.SCOPES)
    
    def __createMessage(self, mensaje):                
        # create email message
        mimeMessage = MIMEMultipart()
        mimeMessage['to'] =  os.getenv("GMAIL_TO")
        mimeMessage['subject'] = 'Permiso de acceso a LEADBRO'
        mimeMessage.attach(MIMEText(mensaje, 'plain'))
 
        return base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
    
    def sendMessage(self, mensaje):
        try:
            raw_string = self.__createMessage(mensaje)
            message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_string}).execute()
            #print("Mensaje enviado con éxito:", message)
            return True, "Se ha notificado al administrador su acceso."
        except HttpError as error:
            # Manejar el error HTTP
            #print("Error al enviar el mensaje:", error)
            return False, "Error inesperado al enviar el mensaje."
        except Exception as error:
            # Manejar otros tipos de errores
            #print("Error inesperado al enviar el mensaje:", error)
            return False, "Error inesperado al enviar el mensaje."