<div align="center">
  <img src="./thumbnail.png" width="800px">
  <h1>🦄 Midas Engine V3: AI Category-Specific Pricing System</h1>
</div>

# 🦄 Midas Engine V3: AI Category-Specific Pricing System
Midas Engine은 단순한 가격 비교를 넘어, AI가 시장 여론과 실거래 데이터를 분석하여 최적의 중고 거래 가격을 제안하는 지능형 자산 가치 분석 플랫폼입니다.

# 🚀 핵심 기능 (Key Features)
## 1. AI 하이브리드 분석 엔진
멀티 모델 지원: Groq(Llama 3.3)의 초고속 성능과 Gemini(2.0 Flash)의 정밀한 추론을 결합한 하이브리드 엔진을 사용합니다.

전문가 페르소나: 차량(딜러), 주택(공인중개사), 도서(수집가) 등 카테고리별 전문 페르소나가 투입되어 여론 데이터를 정밀 분석합니다.

## 2. 고도화된 가격 정제 로직 (Anti-Noise Filter)
데이터 오염 원천 차단: '아반떼 2억'과 같은 오류를 방지하기 위해 장난감, 다이캐스트, 부품, 일괄 매물 등을 걸러내는 강력한 금지어 필터가 작동합니다.

이상치 제거 (IQR Strong): 수집된 데이터의 상하위 15%를 절삭하여 시세 왜곡을 방지하고 순도 높은 평균가를 도출합니다.

만원 단위 자동 보정: 차량 및 부동산 카테고리에서 발생하는 '만원 단위' 표기 오류(예: 2,500)를 실제 원 단위(25,000,000원)로 지능적으로 변환합니다.

## 3. 비즈니스 전략 로직
구매/판매 가격 차별화: 동일한 상품이라도 구매 시에는 '더 싸게 살 수 있는 가격'을, 판매 시에는 '수익을 극대화하는 목표가'를 마진 정책에 따라 다르게 산출합니다.

상황별 마진 가중치: AI가 분석한 시장 상황(Score)에 따라 추천 가격에 유동적인 가중치(0.8x ~ 1.2x)를 부여합니다.

## 4. 지능형 UX 및 위치 기반 서비스
스마트 매장 찾기: 검색된 상품의 카테고리를 자동 인식하여 '중고차 매매단지', '휴대폰 성지', '중고서점' 등 최적화된 오프라인 매장 검색 결과로 연결합니다.

실시간 프로그레스 바: 분석 단계를 시각화하여 데이터 수집부터 AI 분석까지의 과정을 사용자에게 실시간으로 보고합니다.

# 🛠 Tech Stack
### Backend: Flask (Python)

### Database: SQLite & Flask-SQLAlchemy (Search Logs & Price Caching)

### AI: Groq API (Llama 3.3), Google Gemini API (2.5 Flash)

### Crawler: Selenium (Bungae Market), Naver Shopping API

### Frontend: Glassmorphism UI (HTML5, CSS3, JavaScript)

## 📂 프로젝트 구조 (Structure)
### app.py: 비동기 작업 관리 및 Flask 서버 메인 로직

### config.py: API 키 관리 및 구매/판매 마진 정책(MARGINS) 설정

### core/clients.py: 네이버/번개장터 데이터 수집 및 AI 전문가 분석 엔진

### core/service.py: 카테고리별 단위 보정 및 마진 계산 로직 통합

### core/models.py: 데이터 분석을 위한 DB 스키마 정의

### select_model.py: .env 파일에 사용할 AI 모델을 손쉽게 설정하는 CLI 도구

## ⚙️ 설치 및 실행 (Setup)
환경 변수 설정: .env 파일을 생성하고 다음 API 키를 입력합니다.

```bash
NAVER_CLIENT_ID=your_id
NAVER_CLIENT_SECRET=your_secret
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
```
### 의존성 설치:

```bash
pip install -r requirements.txt
```
AI 모델 선택 및 서버 실행:


```bash
python select_model.py
python app.py
```
Developed by Hwang Woo Hyeok 

GitHub: MyosoonHwang/midas_engine
