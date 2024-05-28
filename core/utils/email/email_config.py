from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os



class EMAIL:

    __SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self) -> None:
        self.service = self.__get_gmail_service()
    
    def __get_gmail_service(self):
        credentials_path = "D:\workspace\QBIT\workspace\leadbro\credentials2.json"

        print(credentials_path)

        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, self.__SCOPES)  # Asegúrate de tener tu archivo credentials.json
        creds = flow.run_local_server(port=0)
        service = build('gmail', 'v1', credentials=creds)
        return service

    def __create_message(self, message_text):
        message = MIMEText(message_text)
        message['to'] = "bolisteward18@gmail.com"
        message['from'] = "qbitdashboard@gmail.com"
        message['subject'] = "Acceso a Leadbro"
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_message(self, message_text ):
        try:
            body = self.__create_message(message_text)
            message = self.service.users().messages().send(userId="me", body=body).execute()
            print('Message Id: %s' % message['id'])
            print(message)
            return True,  "Correo enviado exitosamente!."
        
        except Exception as e:
            print('An error occurred: %s' % e)
            return False, "Error al enviar el correo"


        
