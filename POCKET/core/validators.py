from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError("Das Passwort muss mindestens 8 Zeichen lang sein.", code='password_too_short')

        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Das Passwort muss mindestens einen Buchstaben enthalten.", code='password_no_letter')

        if not re.search(r"\d", password):
            raise ValidationError("Das Passwort muss mindestens eine Zahl enthalten.", code='password_no_digit')

        if not re.search(r"[@$!%*?&]", password):
            raise ValidationError("Das Passwort muss mindestens ein Sonderzeichen (@$!%*?&) enthalten.", code='password_no_special')

    def get_help_text(self):
        return "Das Passwort muss mindestens 8 Zeichen lang sein, eine Zahl, einen Buchstaben und ein Sonderzeichen (@$!%*?&) enthalten."
