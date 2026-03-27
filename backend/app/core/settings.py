from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "RiskLens Advanced API"
    database_url: str = "sqlite:///./risklens.db"
    random_seed: int = 42


settings = Settings()
