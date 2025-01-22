errorMessages = {
    "emailValidator": ["შეიყვანეთ სწორი ელ.ფოსტა",
                        "Enter a valid email address."],

    "phoneValidator": ["ტელეფონის ნომერი უნდა იყოს ფორმატში: '+995XXXXXXXXX'", 
                       "Phone number must be entered in the format: '+995XXXXXXXXX'."],

    "emailOrPhoneValidator": ["შეიყვანეთ სწორი ელ.ფოსტა ან ტელეფონის ნომერი",
                              "Enter a valid email or phone number."],

    "emailOrPhoneRequired": ["ელ.ფოსტა ან ტელეფონი აუცილებელია",
                             "Email or Phone is required."],

    "emailOrPhoneExists": ["ელ.ფოსტა ან ტელეფონი უკვე არსებობს",
                           "Email or Phone already exists"],

    "emailExists": ["ელ.ფოსტა უკვე არსებობს",
                    "Email already exists"],

    "phoneExists": ["ტელეფონი უკვე არსებოს",
                    "Phone already exists"],

    "invalidCredentials": ["არასწორი მონაცემები",
                           "Invalid credentials"],
    "passwordRequired": ["პაროლი აუცილებელია",
                         "Password is required"],
}

def get_error_message(messages,key):
    result =messages.get(key, ["უცნობი შეცდომა","Unknown error"])
    return {'ka':result[0],'en':result[1]}


