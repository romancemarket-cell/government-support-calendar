# 정부지원사업 달력 (PC·모바일 반응형 + 일일 자동수집)

이 프로젝트는 **가짜 예시 공고를 넣지 않습니다.** API 인증키가 설정되기 전에는 달력이 비어 있으며, 인증키 설정 후 실제 API에서 받은 공고만 표시합니다.

## 현재 구현
- PC·휴대폰 반응형 월간 달력
- 날짜별 마감 공고와 전체 공고 보기
- 공식 원문 링크, 대상·내용·접수기간 표시
- 기업마당 지원사업정보 API 수집기
- 매일 한국시간 03:00 GitHub Actions 자동 실행
- 대출·융자·정책자금 등 제외 키워드 필터

## 인터넷 공개 및 자동 실행 설정 (최초 1회)
1. GitHub 계정을 만들고 이 폴더 전체를 새 저장소(Repository)에 업로드합니다.
2. 기업마당 API 상세 페이지에서 `사용신청`을 눌러 서비스키를 발급받습니다: https://www.bizinfo.go.kr/apiDetail.do?id=bizinfoApi
3. GitHub 저장소의 **Settings → Secrets and variables → Actions → New repository secret**에서 이름을 `BIZINFO_API_KEY`, 값은 발급받은 키로 저장합니다.
4. 저장소 **Settings → Pages → Build and deployment → Source**에서 `GitHub Actions`를 선택합니다.
5. **Actions** 탭에서 `Daily government support update`를 선택해 `Run workflow`를 한 번 실행합니다.
6. 실행이 성공하면 Pages 주소가 생성됩니다. 그 주소를 PC와 휴대폰 브라우저에서 열면 같은 달력을 볼 수 있습니다.

## 자동 갱신 시간
- 매일 03:00 한국시간 (UTC 18:00)
- Actions 탭에서 수동 실행도 가능
- GitHub Actions 예약 실행은 GitHub 측 부하에 따라 지연될 수 있습니다.

## 데이터 범위와 주의
- 현재 연결된 수집기는 기업마당의 중앙부처·지자체·유관기관 지원사업 API입니다.
- API가 제공하지 않는 공고는 수집되지 않습니다. 전국 모든 기관의 공고를 보장하려면 e나라도움·K-Startup·정부24 등 추가 데이터 소스별 API 권한과 별도 연동이 필요합니다.
- 현재 날짜 필드는 API 응답에서 확인되는 접수마감일을 기준으로 합니다. 날짜를 확인할 수 없는 공고는 달력에서 제외합니다.
- 키워드 필터는 대출/융자성 공고를 제외하기 위한 1차 필터이며, 세부 사업 성격은 원문 확인이 필요합니다.

## 로컬 테스트
Python 3.10 이상에서 `python scripts/collect.py` 실행. `BIZINFO_API_KEY` 환경변수를 먼저 설정해야 합니다. 그 후 `python -m http.server 8000`으로 폴더를 열면 됩니다.
