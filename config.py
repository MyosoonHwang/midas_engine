import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    
    # AI 모델 설정 (최신 안정화 버전)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME = "llama-3.3-70b-versatile"    
    
    # 엔진 선택 우선순위: Groq -> Gemini
    AI_PROVIDER = "groq" if GROQ_API_KEY else "gemini"

    # SQLite 데이터베이스 경로
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'midas.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🚀 구매/판매 모드별 마진 정책 (가격을 다르게 만드는 핵심)
    # AI 점수가 높을수록(유리할수록) 구매는 더 싸게, 판매는 더 비싸게 추천합니다.
    MARGINS = {
        "buy": {"high": 1.0, "normal": 0.9, "low": 0.8},   
        "sell": {"high": 1.2, "normal": 1.1, "low": 0.95}  
    }

    @classmethod
    def check_health(cls):
        print(f"✅ AI 엔진: {cls.AI_PROVIDER.upper()} | DB: SQLite 준비 완료")