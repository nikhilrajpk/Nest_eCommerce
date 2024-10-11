import re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class Authentication_check:
    def email_validator(self,email):
        if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$', email):
            return 'Email should be valid!'
        return None
            
    def first_name_validator(self,first_name):
        if any(char.isdigit() or char.isspace() for char in first_name):
            return 'First name should not contain number or spaces!'
        return None
        
    def last_name_validator(self,last_name):
        if any(char.isdigit() or char.isspace() for char in last_name):
            return 'Last name should not contain number or spaces!'
        return None
    
    def pass_validator(self,password):
        try:
            validate_password(password)
        except ValidationError as e:
            return e.messages
        return None
    def password_mismatch(self,password, confirm_password):
        if password != confirm_password:
            return 'Passwords do not match'
        return None