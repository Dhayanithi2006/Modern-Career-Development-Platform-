from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

print("START")

h = pwd_context.hash("dracid123")

print("HASH:", h)
