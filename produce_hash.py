import hashlib

def generate_sha256_hash(input_string):
  """
  Generates the SHA256 hash of a given string.

  Args:
    input_string: The string to be hashed.

  Returns:
    The hexadecimal representation of the SHA256 hash.
  """
  # Create a new sha256 hash object
  sha256_hash = hashlib.sha256()

  # Update the hash object with the bytes-like object (encoded string)
  # It's crucial to encode the string to bytes, as hash functions operate on bytes.
  sha256_hash.update(input_string.encode('utf-8'))

  # Return the hexadecimal digest of the hash
  return sha256_hash.hexdigest()

# Example usage:
data_to_hash = "hello"
#data_to_hash = "This is a test string for SHA256 hashing."
hashed_value = generate_sha256_hash(data_to_hash)

print(f"Original string: {data_to_hash}")
print(f"SHA256 Hash: {hashed_value}")

# You can also directly hash a string without a function:
another_string = "Another example."
direct_hash = hashlib.sha256(another_string.encode('utf-8')).hexdigest()
print(f"Direct hash of '{another_string}': {direct_hash}")
