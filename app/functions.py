def encrypt(password):
    encpass = ""
    for ch in password:
        asc = ord(ch) + 3
        ench = chr(asc)
        encpass += ench
    return encpass[::-1]

def decrypt(password):
    decpass = ""
    for ch in password:
        asc = ord(ch) - 3
        decch = chr(asc)
        decpass += decch
    return decpass[::-1]

decpassword = "Abcd"
encpassword = "gfeD"

print(encrypt(decpassword))
print(decrypt(encpassword))


