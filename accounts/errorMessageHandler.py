errorMessages = {
    "emailValidator": ["შეიყვანეთ სწორი ელ.ფოსტა",
                        "Enter a valid email address."],

    "phoneValidator": ["ტელეფონის ნომერი უნდა იყოს ფორმატში: '+995XXXXXXXXX'", 
                       "Phone number must be entered in the format: '+995XXXXXXXXX'."],

    "emailOrPhoneValidator": ["შეიყვანეთ სწორი ელ.ფოსტა ან ტელეფონის ნომერი",
                              "Enter a valid email or phone number."],

    "emailOrPhoneRequired": ["ელ.ფოსტა ან ტელეფონი აუცილებელია",
                             "Email or Phone is required."],
    "emailOrPhoneBlank" : ["ელ.ფოსტა ან ტელეფონი არ შეიძლება იყოს ცარიელი",
                           "Email or phone cannot be blank."],

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
                         
    "passwordBlank": ["პაროლი არ შეიძლება იყოს ცარიელი",
                      "Password cannot be blank"],

    "userExcist": ["მომხმარებელი უკვე არსებობს",
                   "User already exists"],

    "passwordsNotMatch": ["პაროლები არ ემთხვევა",
                          "Passwords do not match"],
}

def get_error_message(messages,key):
    result =messages.get(key, ["უცნობი შეცდომა","Unknown error"])
    return {'ka':result[0],'en':result[1]}


