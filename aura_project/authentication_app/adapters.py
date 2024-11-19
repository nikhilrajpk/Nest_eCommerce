from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from authentication_app.models import CustomUser

from django.urls import reverse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        print("Entering pre_social_login method")  # Debug line
        # Clear success messages if they exist
        for message in messages.get_messages(request):
            if message.level == messages.SUCCESS:
                # This removes any success messages
                message.delete()
                
        user = sociallogin.user
        if user.email:
            try:
                custom_user = CustomUser.objects.get(email=user.email)
                # Check if the account is blocked
                if custom_user.is_block:
                    print(f'Logging out blocked user: {custom_user.first_name}')
                    
                    # Log the user out using Django's logout method
                    logout(request)
                    request.session.flush() 
                    request.session['account_blocked'] = True
                    
                    # Add error message to show on the login page
                    messages.error(request, "Your account is blocked by the admin. Please contact support.")
                    
                    # Redirect the user back to the login page
                    return redirect(reverse('authentication_app:login'))  # Using reverse to ensure proper redirection
                
            except CustomUser.DoesNotExist:
                # If the user doesn't exist, continue with the social login
                pass
