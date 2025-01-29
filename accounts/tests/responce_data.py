from ..errorMessageHandler import errorMessages, get_error_message
no_data_registration={
    "email_or_phone": [get_error_message(errorMessages,"emailOrPhoneRequired")],
    "password": [get_error_message(errorMessages,"passwordRequired")],
    "password2": [get_error_message(errorMessages,"passwordRequired")]
}
only_email_provided_registration={
    "password": [get_error_message(errorMessages,"passwordRequired")],
    "password2": [get_error_message(errorMessages,"passwordRequired")]
}

only_email_and_password_provided_registration={
    "password2": [get_error_message(errorMessages,"passwordRequired")]
}
only_email_and_password2_provided_registration={
    "password": [get_error_message(errorMessages,"passwordRequired")]
}
only_passwords_provided_registration={
    "email_or_phone": [get_error_message(errorMessages,"emailOrPhoneRequired")]
}

invalid_email_registration={
    "email_or_phone": [get_error_message(errorMessages,"emailOrPhoneValidator")]
}
password_missmatch={
    "password": [get_error_message(errorMessages,"passwordsNotMatch")]
}
