import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ASTRA_DB_APPLICATION_TOKEN: str = os.getenv("ASTRA_DB_APPLICATION_TOKEN", "")
    ASTRA_DB_API_ENDPOINT: str = os.getenv("ASTRA_DB_API_ENDPOINT", "")
    ASTRA_DB_KEYSPACE: str = os.getenv("ASTRA_DB_KEYSPACE", "admintpe_v1")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_SHORT_MODEL: str = os.getenv("LLM_SHORT_MODEL", "llama-3.3-70b-versatile")

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    LLM_LONG_MODEL: str = os.getenv("LLM_LONG_MODEL", "gemini-1.5-flash")

    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    WORKFLOW_VERSION: str = os.getenv("WORKFLOW_VERSION", "baseline_security_mode")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def validate(self) -> list[str]:
        missing = []
        if not self.ASTRA_DB_APPLICATION_TOKEN:
            missing.append("ASTRA_DB_APPLICATION_TOKEN")
        if not self.ASTRA_DB_API_ENDPOINT:
            missing.append("ASTRA_DB_API_ENDPOINT")
        if not self.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not self.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        return missing


settings = Settings()
