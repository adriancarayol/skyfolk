from django import forms
from feedback.models import Feedback
from mailer.mailer import Mailer


class ContactForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        labels = {
            'subject': 'Asunto',
            'message': 'Mensaje'
        }
    
    def send_email(self):
        email = self.cleaned_data['email']
        message = self.cleaned_data['message']
        mail = Mailer()
        mail.send_messages('Skyfolk - Hemos recibido tus comentarios.', template='emails/contact_message_received.html',
                           context={'email': email, 'message': message}, to_emails=(email,))
