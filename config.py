import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash") # 최신 안정화 모델

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "llama-3.3-70b-versatile"    
    
    AI_PROVIDER = "groq" if GROQ_API_KEY else "gemini"

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'midas.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🚀 카테고리별 기본 마진 정책
    MARGINS = {
        "buy": {"high": 1.0, "normal": 0.9, "low": 0.8}, # 구매는 더 싸게 유도
        "sell": {"high": 1.2, "normal": 1.1, "low": 0.95} # 판매는 더 비싸게 유도
    }

    @classmethod
    def check_health(cls):
        print(f"✅ AI 엔진: {cls.AI_PROVIDER.upper()} | DB: SQLite 연결 준비 완료")