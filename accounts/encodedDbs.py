import base64
key = "welsecurerenukaSofttech"
def encode_string(text):
    encoded_chars = []
    key_index = 0
    for char in text:
        # Apply substitution by adding the key value to the character ASCII code
        encoded_char = chr((ord(char) + ord(key[key_index])) % 256)
        encoded_chars.append(encoded_char)
        # Move to the next key character (wrap around if needed)
        key_index = (key_index + 1) % len(key)
    # Join the encoded characters and base64 encode the result for better representation
    encoded_text = base64.b64encode("".join(encoded_chars).encode()).decode()
    return encoded_text

def decode_string(encoded_text):
    # Decode the base64 encoded string
    decoded_chars = base64.b64decode(encoded_text).decode()
    decoded_text = ""
    key_index = 0
    for char in decoded_chars:
        # Apply reverse substitution by subtracting the key value from the character ASCII code
        decoded_char = chr((ord(char) - ord(key[key_index])) % 256)
        decoded_text += decoded_char
        # Move to the next key character (wrap around if needed)
        key_index = (key_index + 1) % len(key)
    return decoded_text

# Example usage
original_string = "wjosoooooo"


# Encode the original string
encoded_string = encode_string(original_string)
print("Encoded string:", encoded_string)

# Decode the encoded string
decoded_string = decode_string(encoded_string)
print("Decoded string:", decoded_string)

# Verify if the decoded string matches the original string
print("Matched:", original_string == decoded_string)
