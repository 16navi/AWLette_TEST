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

dict1_list = []

my_dict1 = {
    1 : dict1_list
    }

print(my_dict1)

dict1_list.append(1)
dict1_list.append(2)

print(my_dict1)