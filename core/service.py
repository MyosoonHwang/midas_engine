from core.clients import NaverShoppingClient, BungaeClient, AIAnalyst
from core.models import db, SearchLog, PriceRecord
from config import Config
from datetime import datetime, timedelta

class MidasService:
    def __init__(self):
        self.naver = NaverShoppingClient()
        self.bungae = BungaeClient()
        self.ai = AIAnalyst()

    def get_analysis(self, product, mode, category, progress_callback=None):
        # 1. 라이브 데이터 수집
        if progress_callback: progress_callback(20, "네이버 쇼핑 분석 중...")
        n_data = self.naver.search_products(product, category)
        
        if progress_callback: progress_callback(40, "번개장터 매물 크롤링 중...")
        b_data = self.bungae.search_products(product, category)
        
        n_p, b_p = (n_data['avg'] if n_data else 0), (b_data['avg'] if b_data else 0)
        raw_avg = (n_p + b_p)//2 if n_p and b_p else (n_p or b_p)

        # 2. AI 시세 교정
        if progress_callback: progress_callback(70, "AI 전문가 정밀 감정 중...")
        reviews = self.naver.search_blog_reviews(product)
        ai_res = self.ai.analyze_sentiment(product, reviews, raw_avg, category, mode)
        
        base_price = ai_res.get('estimated_price', raw_avg)
        score = ai_res.get('score', 0)

        # 3. ⚖️ 모드별 가격 차별화 로직
        policy = Config.MARGINS[mode]
        if score >= 5: target_price = int(base_price * policy['high'])
        elif score <= -3: target_price = int(base_price * policy['low'])
        else: target_price = int(base_price * policy['normal'])

        # 4. DB 저장
        try:
            db.session.add(PriceRecord(keyword=product, category=category, naver_price=n_p, bungae_price=b_p, 
                                      ai_estimated_price=base_price, ai_score=score, ai_reason=ai_res.get('reason')))
            db.session.add(SearchLog(keyword=product, mode=mode, category=category))
            db.session.commit()
        except: db.session.rollback()

        return {
            "product": product, "mode": mode, "category": category,
            "market_price": {"avg": n_p}, "bungae_price": {"avg": b_p},
            "ai_analysis": ai_res, "recommendation": {"target_price": target_price}
        }

midas_engine = MidasService()