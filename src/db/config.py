from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения, читаются из переменных окружения и файла .env.
    """

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    ES_HOST: str = "localhost"
    ES_PORT: str = "9200"
    ES_INDEX: str = "documents"
    ES_DOCS_LIMIT: int = 20
    ES_SCROLL_SIZE: int = 500

    @property
    def DATABASE_URL_asyncpg(self):
        """
        Строка подключения к PostgreSQL для драйвера asyncpg.
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def ELASTICSEARCH_URL(self) -> str:
        """
        Адрес Elasticsearch для асинхронного клиента.
        """
        return f"http://{self.ES_HOST}:{self.ES_PORT}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
