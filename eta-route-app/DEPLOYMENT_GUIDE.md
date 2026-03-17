# 🚀 Streamlit Community Cloud 배포 가이드

이 문서는 **eta-route-app**을 Streamlit Community Cloud에 배포하는
단계별 안내서입니다. 초보자도 따라할 수 있도록 설명합니다.

---

## 📋 배포 전 체크리스트

배포에 필요한 파일이 모두 있는지 확인하세요:

```
eta-route-app/
├── app.py                  ✅ 메인 앱 (필수)
├── requirements.txt        ✅ 패키지 목록 (필수)
├── api/
│   ├── __init__.py         ✅ 패키지 초기화 파일
│   └── ais_client.py       ✅ API 클라이언트
├── utils/
│   ├── __init__.py         ✅ 패키지 초기화 파일
│   ├── data_processing.py  ✅ 데이터 처리
│   └── eta_calculator.py   ✅ ETA 계산
├── components/
│   ├── __init__.py         ✅ 패키지 초기화 파일
│   ├── map_view.py         ✅ 지도 시각화
│   └── data_table.py       ✅ 데이터 테이블
├── .gitignore              ✅ Git 제외 파일
└── README.md               ✅ 프로젝트 설명
```

⚠️ **`__init__.py`** 파일이 각 폴더에 반드시 있어야 합니다!
   (비어있는 파일이어도 됩니다)

⚠️ **`.venv/` 폴더는 업로드하지 마세요!** `.gitignore`에서 자동 제외됩니다.

---

## Step 1: GitHub 계정 준비

1. [github.com](https://github.com)에 가입 (이미 있으면 건너뜀)
2. 로그인

---

## Step 2: GitHub Repository 생성

1. GitHub에서 **"+"** 버튼 → **"New repository"** 클릭
2. 설정:
   - Repository name: `eta-route-app`
   - Description: `AIS 선박 위치 추적 & ETA 계산 Streamlit 웹앱`
   - **Public** 선택 (Streamlit Cloud 무료 배포는 Public만 가능)
   - ❌ "Add a README file" 체크 해제 (이미 README가 있으므로)
3. **"Create repository"** 클릭

---

## Step 3: 프로젝트를 GitHub에 업로드

터미널에서 아래 명령어를 순서대로 실행하세요:

```bash
# 1. 프로젝트 폴더로 이동
cd /Users/sihyeon/Developer/Antigravity/Shipping_ETA/eta-route-app

# 2. Git 초기화
git init

# 3. 모든 파일을 Git에 추가
git add .

# 4. 첫 번째 커밋
git commit -m "🚢 eta-route-app 초기 버전"

# 5. 메인 브랜치 이름 설정
git branch -M main

# 6. GitHub 리포지토리 연결 (⚠️ 아래 URL을 자신의 GitHub 주소로 변경!)
git remote add origin https://github.com/YOUR_USERNAME/eta-route-app.git

# 7. GitHub에 업로드
git push -u origin main
```

> 💡 `YOUR_USERNAME` 부분을 본인의 GitHub 사용자 이름으로 바꿔주세요!

---

## Step 4: Streamlit Community Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io)에 접속
2. **"Sign in with GitHub"**으로 로그인
3. **"New app"** 클릭
4. 설정 입력:

   | 항목 | 입력값 |
   |------|--------|
   | Repository | `YOUR_USERNAME/eta-route-app` |
   | Branch | `main` |
   | Main file path | `app.py` |

5. **"Deploy!"** 클릭
6. 약 2~3분 후 앱이 배포됩니다! 🎉

---

## Step 5: 배포 완료 확인

배포가 완료되면 아래와 같은 URL이 생성됩니다:

```
https://YOUR_USERNAME-eta-route-app-app-XXXX.streamlit.app
```

이 URL을 친구에게 공유하면 누구나 접속할 수 있습니다!

---

## 🔧 자주 만나는 문제

### Q1: "ModuleNotFoundError" 에러가 뜹니다
→ `requirements.txt`에 해당 패키지가 있는지 확인하세요.

### Q2: 배포했는데 화면이 안 나옵니다
→ Streamlit Cloud 대시보드에서 로그(Logs)를 확인하세요.
   API 호출 실패일 수 있습니다.

### Q3: 코드를 수정하면 자동으로 반영되나요?
→ 네! GitHub에 `git push`하면 Streamlit Cloud가 자동으로 다시 배포합니다.

### Q4: Private repository도 배포 가능한가요?
→ 무료 플랜에서는 **Public repository만** 가능합니다.

---

## 📝 코드 수정 후 업데이트 방법

```bash
# 1. 수정된 파일 추가
git add .

# 2. 커밋 메시지 작성
git commit -m "기능 추가: ○○○ 수정"

# 3. GitHub에 업로드 (자동으로 Streamlit Cloud에 반영)
git push
```
