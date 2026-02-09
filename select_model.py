import os
from dotenv import load_dotenv

# 1. 환경 변수 로드 (API 키 확인용)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ✅ 구글 공식 문서 기반 최신 모델 리스트 (하드코딩)
# API 호출 없이 바로 선택할 수 있게 만들었습니다.
AVAILABLE_MODELS = [
    {"name": "gemini-3-pro-preview", "desc": "최고 성능, 멀티모달 추론 (New!)"},
    {"name": "gemini-3-flash-preview", "desc": "속도와 성능의 균형 (Balanced)"},
    {"name": "gemini-2.5-flash", "desc": "가성비 최고, 빠르고 안정적 (추천)"},
    {"name": "gemini-2.5-pro", "desc": "고성능 추론 모델 (Stable)"},
    {"name": "gemini-2.5-flash-lite", "desc": "초고속, 저비용 모델"},
    {"name": "gemini-2.0-flash", "desc": "이전 세대 모델 (구관이 명관)"}
]

def update_env_file(key, value):
    """ .env 파일 업데이트 함수 """
    env_path = '.env'
    new_lines = []
    key_found = False
    
    # .env 파일이 없으면 새로 생성
    if not os.path.exists(env_path):
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("")
    
    # 기존 파일 읽기
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                key_found = True
            else:
                new_lines.append(line)
    
    # 키가 없었다면 새로 추가
    if not key_found:
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines.append('\n')
        new_lines.append(f"{key}={value}\n")
        
    # 파일 다시 쓰기
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"\n✅ 설정 저장 완료! .env 파일에 다음 내용이 저장되었습니다:")
    print(f"👉 {key}={value}")

# 메인 로직
def main():
    print("\n🦄 Midas Engine AI 모델 선택기")
    print("========================================")
    
    for i, model in enumerate(AVAILABLE_MODELS):
        print(f"[{i+1}] {model['name']:<25} | {model['desc']}")
    print("========================================")
    
    while True:
        try:
            selection = input(f"\n🚀 사용할 모델의 번호를 입력하세요 (1~{len(AVAILABLE_MODELS)}): ")
            idx = int(selection) - 1
            
            if 0 <= idx < len(AVAILABLE_MODELS):
                selected_model = AVAILABLE_MODELS[idx]['name']
                print(f"\n👌 선택된 모델: {selected_model}")
                update_env_file("GEMINI_MODEL_NAME", selected_model)
                print("\n🎉 준비 완료! 이제 'python app.py'를 실행하세요.")
                break
            else:
                print("❌ 잘못된 번호입니다. 다시 입력해주세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")

if __name__ == "__main__":
    main()