import os


class Settings:
    def __init__(self):
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey123")
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

settings = Settings()
