from pydantic_settings import BaseSettings


class Config(BaseSettings):    
    TG_BOT_TOKEN: str
    API_BASE: str
    API_USER: str
    API_PASS: str
    
    class Config:
        env_file = ".env"

config = Config()
