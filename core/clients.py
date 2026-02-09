import urllib.request, json, statistics, time, re
from groq import Groq
from google import genai
from config import Config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def clean_and_filter_prices(items, category):
    """불순물(장난감, 부품)을 제거하고 가격만 추출"""
    # 🚫 금지어 리스트
    forbidden = ["장난감", "다이캐스트", "매트", "키케이스", "미니어처", "부품", "폐차", "일괄", "박스", "케이스"]
    
    prices = []
    for item in items:
        title = item.get('title', '').lower()
        price = int(item.get('lprice', 0))
        
        # 1. 금지어 포함 매물 제거
        if any(f in title for f in forbidden): continue
        
        # 2. 터무니없는 가격 1차 필터 (예: 차량인데 10만원 미만 등)
        if category == 'car' and price < 500000: continue
        
        if price > 1000: prices.append(price)
    
    return prices

def remove_outliers_advanced(prices):
    if len(prices) < 5: return prices
    prices.sort()
    # 상하위 15% 절삭하여 더 깨끗한 데이터 확보
    cut = int(len(prices) * 0.15)
    return prices[cut:-cut]

class NaverShoppingClient:
    def search_products(self, keyword, category):
        url = f"https://openapi.naver.com/v1/search/shop.json?query={urllib.parse.quote(keyword)}&display=100&sort=sim"
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", Config.NAVER_CLIENT_ID)
        req.add_header("X-Naver-Client-Secret", Config.NAVER_CLIENT_SECRET)
        try:
            res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            items = res.get('items', [])
            if not items: return None
            
            # 🔥 필터링 적용
            prices = clean_and_filter_prices(items, category)
            valid_prices = remove_outliers_advanced(prices)
            
            if not valid_prices: return None
            return {"avg": int(statistics.median(valid_prices)), "category": items[0].get('category3', '기타')}
        except: return None

    def search_blog_reviews(self, keyword):
        url = f"https://openapi.naver.com/v1/search/blog?query={urllib.parse.quote(keyword)}&display=15&sort=sim"
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", Config.NAVER_CLIENT_ID)
        req.add_header("X-Naver-Client-Secret", Config.NAVER_CLIENT_SECRET)
        try:
            res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
            return "\n".join([f"- {i['title']}: {i['description']}" for i in res.get('items', [])])
        except: return ""

class BungaeClient:
    def search_products(self, keyword, category):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=opts)
        try:
            driver.get(f"https://m.bunjang.co.kr/search/products?q={keyword}")
            time.sleep(2)
            cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
            prices = []
            for c in cards:
                m = re.findall(r'(\d{1,3}(?:,\d{3})+)', c.text)
                if m:
                    p = int(m[0].replace(",", ""))
                    # 🚗 차량 단위 보정 (번개장터는 2500만원을 2,500으로 적는 경우 많음)
                    if category == 'car' and p < 10000: p *= 10000 
                    prices.append(p)
            valid = remove_outliers_advanced(prices)
            return {"avg": int(statistics.median(valid))} if valid else None
        finally: driver.quit()

class AIAnalyst:
    def analyze_sentiment(self, product, reviews, current_price, category, mode):
        # 🤖 AI 페르소나와 논리 강화
        guides = {
            'car': "중고차 감정사입니다. 사고 유무, 연식 감가를 고려하세요.",
            'house': "부동산 전문가입니다. 실거래가와 호가 차이를 분석하세요.",
            'cloth': "리셀 전문가입니다. 프리미엄이나 가품 여부를 분석하세요."
        }
        prompt = f"""
        [전문가 페르소나]: {guides.get(category, '시장 데이터 분석가')}
        [대상]: {product} | [현재 평균가]: {current_price}원 | [모드]: {mode}
        [데이터]: {reviews[:2500]}
        
        [필수 미션]
        1. 현재 평균가가 상식적인지 판단하고, 아니라면 당신의 지식으로 '진짜 시세'를 정하세요.
        2. {mode} 입장에서 이득인 상황인지 -10 ~ 10점으로 점수를 주세요.
        3. 반드시 JSON으로만 답하세요. 
        JSON: {{ "score": 숫자, "reason": "논리적 근거(3문장)", "estimated_price": 실제적정가숫자 }}
        """
        try:
            if Config.AI_PROVIDER == "groq":
                client = Groq(api_key=Config.GROQ_API_KEY)
                res = client.chat.completions.create(model=Config.GROQ_MODEL_NAME, messages=[{"role":"user", "content":prompt}], response_format={"type":"json_object"})
                return json.loads(res.choices[0].message.content)
            else:
                client = genai.Client(api_key=Config.GEMINI_API_KEY)
                res = client.models.generate_content(model=Config.GEMINI_MODEL_NAME, contents=prompt, config={'response_mime_type':'application/json'})
                return json.loads(res.text)
        except: return {"score":0, "reason":"분석 실패", "estimated_price": current_price}