def encrypt(password):
    encpass = ""
    for ch in password:
        asc = ord(ch) + 3
        ench = chr(asc)
        encpass += ench
    return encpass[::-1]