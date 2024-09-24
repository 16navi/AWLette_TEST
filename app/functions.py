import random, string


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


def generate_code(n):
    my_list = []
    my_list.extend(''.join(random.choice(string.ascii_uppercase) for _ in range(n)) + ''.join(random.choice(string.digits) for _ in range(n)))
    random.shuffle(my_list)
    return ''.join(my_list)