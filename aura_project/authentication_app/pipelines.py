def save_user_details(backend, user, response, *args, **kwargs):
    """
    Custom pipeline step to save email and first_name from Google response.
    """
    if backend.name == 'google':
        email = response.get('email')
        first_name = response.get('given_name')
        last_name = response.get('family_name')

        # Save email if it's not already set
        if email and not user.email:
            user.email = email
        # Save first name if it's not already set
        if first_name and not user.first_name:
            user.first_name = first_name
        # Optionally save last name too
        if last_name and not user.last_name:
            user.last_name = last_name
        # Save the user to the database
        user.save()
