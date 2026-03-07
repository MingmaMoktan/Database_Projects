import hashlib
import os

# ----
# 1/6: Plain-text storage
# ----

'''
password = "hello"
print(f"\n1/6: {password}")
'''

# ----
# 2/6: Basic Encryption / Caesars Cipher
# ----
def caesar_cipher(message, shift):
    encrypted_message = ""
    for char in message:
        if char.isalpha():
            # Determine the new character by shifting it by the specified amount
            shifted_char = chr((ord(char.lower()) - 97 + shift) % 26 + 97)
            # Preserve the original case of the character
            if char.isupper(): shifted_char = shifted_char.upper()
            encrypted_message += shifted_char
        else:
            # Preserve non-letter characters
            encrypted_message += char
    return encrypted_message

'''
caesar_encrypted = caesar_cipher("hello", 1)
print(f"\n2/6: {caesar_encrypted}")
'''

# ----
# 3/6: MD5
# ----
def hash_password_md5(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()

'''
password = "hello"
md5_hashing = hash_password_md5(password)
print(f"\n3/6: MD-5")
print("Password: ", password)
print("Hashed password:" , md5_hashing)
'''

# ----
# 3/6: Sha1
# ----
def hash_password_sha1(password):
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    return sha1.hexdigest()

'''
password = "hello"
sha1_hashing = hash_password_sha1(password)
print(f"\n3/6: SHA-1")
print("Password: ", password)
print("Hashed password:" , sha1_hashing)
'''

# ----
# 4/6: Hashing with Salt (md-5 and salt)
# ----
def hash_password_md5(password, salt):
    md5 = hashlib.md5()
    salt_and_password = salt + password
    md5.update(salt_and_password.encode('utf-8'))
    return md5.hexdigest()

'''
salt = "abc123"
password = "hello"
hashed_password = hash_password_md5(password, salt)

print("\n4/6:")
print("Password:", password)
print("Salt:", salt)
print("Password and salt combined:", (salt + password))
print("Hashed password:", hashed_password)
'''

# ----
# 5/6: Hashing with Salt and Iterations (md-5 and salt and iterations)
# ----
def hash_password_md5(password, salt, iterations):
    hashed_password = (salt + password).encode('utf-8')

    # Keep hashing the hashed output for the amount of iterations
    for _ in range(iterations):
        hashed_password = hashlib.md5(hashed_password).digest()

    return hashed_password.hex()

'''
salt = "abc123"
password = "hello"
iterations = 100000
hashed_password = hash_password_md5(password, salt, iterations)

print("\n5/6:")
print("Password:", password)
print("Salt:", salt)
print("Iterations:", iterations)
print("Password and salt combined:", (salt + password))
print("Hashed password:", hashed_password)
'''

# ----
# 6/6: Adaptive Hashing Algorithms (Bcrypt)
# Note: Need to install bcrypt package: pip3 install bcrypt
# One of the more newer (and more secure) libraries are for example: argon2 (from 2015)
# ----

import bcrypt

def hash_password_bcrypt(password, salt):
    # Hash the password using the generated salt.
    # The salt already contains the number of rounds, so bcrypt will apply the correct cost automatically.
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # hashed_password is in format like: "$2b$12$B02ey1qPwkcD.jo9jvPJxejPLU/G1tpcHSnvUQlZZES.xsR2hjK.2"
    # $2b$ = bcrypt version
    # $12$ = cost factor (log2 number of rounds)
    # salt (22 characters after those above): B02ey1qPwkcD.jo9jvPJxe
    # hashed password: jPLU/G1tpcHSnvUQlZZES.xsR2hjK.2
    return hashed_password

def verify_password_bcrypt(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

'''
cost = 12 # cost factor (2^12 rounds = 4096 rounds)
# Generate a salt with the specified number of rounds (cost factor).
# The salt will contain bcrypt version, number of rounds and the actual salt
salt = bcrypt.gensalt(rounds=cost)
password = "hello"

# Hash the password
hashed_password = hash_password_bcrypt(password, salt)
print("\n6/6:")
print("Password:", password)
print("Salt (bcrypt version, rounds, salt):", salt)
print("Salt and password combined:", (str(salt) + password))
print("Hashed password:", hashed_password)

# Verify the password
password_to_check = "hello"
is_valid = verify_password_bcrypt(password_to_check, hashed_password)
print("Is the password valid?", is_valid)
'''