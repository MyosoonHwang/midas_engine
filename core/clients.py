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

def filter_bad_data(items, category):
    """장난감, 부품, 일괄 매물 등 시세 왜곡 데이터 원천 차단"""
    forbidden = ["장난감", "다이캐스트", "매트", "키케이스", "미니어처", "부품", "폐차", "일괄", "박스", "케이스"]
    prices = []
    for item in items:
        title = item.get('title', '').lower()
        price = int(item.get('lprice', 0))
        
        # 1. 금지어 필터링
        if any(f in title for f in forbidden): continue
        # 2. 차량 카테고리 최소가 제한 (50만원 미만은 부품으로 간주)
        if category == 'car' and price < 500000: continue
        
        if price > 1000: prices.append(price)
    return prices

def remove_outliers_strong(prices):
    """상하위 15%를 잘라내어 극단적 이상치 제거"""
    if len(prices) < 5: return prices
    prices.sort()
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
            prices = filter_bad_data(items, category)
            valid = remove_outliers_strong(prices)
            if not valid: return None
            return {"avg": int(statistics.median(valid)), "category": items[0].get('category3', '기타')}
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
    """⚡ 번개장터 크롤러 (차량 단위 보정 로직 포함)"""
    def search_products(self, keyword, category):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=opts)
        try:
            driver.get(f"https://m.bunjang.co.kr/search/products?q={keyword}")
            time.sleep(2)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/products/']")))
            cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
            prices = []
            for c in cards:
                m = re.findall(r'(\d{1,3}(?:,\d{3})+)', c.text)
                if m:
                    p = int(m[0].replace(",", ""))
                    # 🚗 차량 단위 보정 (2,500 등으로 적힌 만원 단위를 원 단위로 변환)
                    if category == 'car' and p < 10000: p *= 10000 
                    prices.append(p)
            valid = remove_outliers_strong(prices)
            return {"avg": int(statistics.median(valid))} if valid else None
        except: return None
        finally: driver.quit()

class AIAnalyst:
    def analyze_sentiment(self, product, reviews, avg_price, category, mode):
        guides = {
            'car': "자동차 감정사입니다. 연식과 주행거리를 고려하여 만원 단위 오류를 교정하세요.",
            'house': "부동산 전문가입니다. 실거래가와 호가 차이를 분석하세요.",
            'cloth': "리셀러입니다. 정품 여부와 시장 수요를 분석하세요."
        }
        prompt = f"""당신은 {category} 전문가입니다. 여론:{reviews[:2500]} 가이드:{guides.get(category, '시세 분석')}
        현재 기계적 평균가: {avg_price}원. 데이터가 터무니없다면(예: 아반떼 2억) 무시하고 진짜 시세를 제안하세요.
        반드시 JSON만 출력: {{ "score": -10~10, "reason": "3문장 분석", "estimated_price": 숫자 }}"""
        
        try:
            if Config.AI_PROVIDER == "groq":
                client = Groq(api_key=Config.GROQ_API_KEY)
                res = client.chat.completions.create(model=Config.GROQ_MODEL_NAME, messages=[{"role":"user", "content":prompt}], response_format={"type":"json_object"})
                return json.loads(res.choices[0].message.content)
            else:
                client = genai.Client(api_key=Config.GEMINI_API_KEY)
                res = client.models.generate_content(model=Config.GEMINI_MODEL_NAME, contents=prompt, config={'response_mime_type':'application/json'})
                return json.loads(res.text)
        except: return {"score":0, "reason":"AI 분석 오류", "estimated_price": avg_price}