from werkzeug.security import generate_password_hash

new_password = "M@smas!2"  # Replace with your desired password
hashed_password = generate_password_hash(new_password)
print(hashed_password)