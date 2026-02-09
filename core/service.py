from core.clients import NaverShoppingClient, BungaeClient, AIAnalyst
from core.models import db, SearchLog, PriceRecord
from config import Config
from datetime import datetime, timedelta

class MidasService:
    def __init__(self):
        self.naver, self.bungae, self.ai = NaverShoppingClient(), BungaeClient(), AIAnalyst()

    def get_analysis(self, product, mode, category, progress_callback=None):
        # 1. 라이브 데이터 수집
        if progress_callback: progress_callback(20, "시장 매물 전수 조사 중...")
        n_data = self.naver.search_products(product, category)
        b_data = self.bungae.search_products(product, category)
        
        n_p = n_data['avg'] if n_data else 0
        b_p = b_data['avg'] if b_data else 0
        raw_avg = (n_p + b_p) // 2 if n_p and b_p else (n_p or b_p)

        # 2. AI 정밀 시세 교정
        if progress_callback: progress_callback(60, "AI 전문가 시세 감정 중...")
        reviews = self.naver.search_blog_reviews(product)
        ai_res = self.ai.analyze_sentiment(product, reviews, raw_avg, category, mode)
        
        base_price = ai_res.get('estimated_price', raw_avg)
        score = ai_res.get('score', 0)

        # 3. ⚖️ 구매/판매 마진 분리 로직 (가장 중요!)
        policy = Config.MARGINS[mode]
        if score >= 5: # 아주 유리한 상황
            target_price = int(base_price * policy['high'])
        elif score <= -3: # 아주 불리한 상황
            target_price = int(base_price * policy['low'])
        else: # 보통
            target_price = int(base_price * policy['normal'])

        # 4. 결과 저장
        try:
            db.session.add(SearchLog(keyword=product, mode=mode, category=category))
            db.session.add(PriceRecord(keyword=product, category=category, naver_price=n_p, bungae_price=b_p, 
                                      ai_estimated_price=base_price, ai_score=score, ai_reason=ai_res.get('reason')))
            db.session.commit()
        except: db.session.rollback()

        return {
            "product": product, "mode": mode, "category": category,
            "market_price": {"avg": n_p}, "bungae_price": {"avg": b_p},
            "ai_analysis": ai_res, "recommendation": {"target_price": target_price}
        }

midas_engine = MidasService()