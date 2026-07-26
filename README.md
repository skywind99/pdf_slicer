# ✂️ Auto PDF Slicer

> 스캔 답안지 PDF를 학생별로 자동 분할하는 교사용 데스크탑 앱

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-2563EB?style=flat)
![PyMuPDF](https://img.shields.io/badge/PDF-PyMuPDF-EF4444?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 📌 개요

시험 후 스캔한 전체 답안지 PDF를 **학생 1인당 N페이지** 단위로 자동 분할하고,
`10901_수학.pdf` 형태의 파일명으로 저장하는 Windows 앱입니다.

기존 수작업(Adobe Acrobat으로 한 명씩 잘라내기)을 **완전 자동화**합니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 📄 PDF 미리보기 | 선택한 PDF를 앱 내에서 바로 확인, 마우스 휠로 페이지 이동 |
| ✂️ 일괄 분할 | 전체 PDF를 N페이지 간격으로 자동 분할 |
| 🏷️ 자동 파일명 | `학년반 + 번호(01~) + 접미어` 형태로 자동 생성 |
| 📁 폴더 자동 생성 | 원본 파일 위치에 `분할완료/` 폴더 자동 생성 |
| 🚀 완료 후 폴더 오픈 | 분할 완료 시 저장 폴더 자동으로 열림 |

---

## 🖥️ 스크린샷

```
┌─────────────────────────────────────────────────────┐
│  ✂ PDF Slicer        │                              │
│  스캔 답안지 자동 분할기  │      [PDF 미리보기]           │
│                        │                              │
│  ① 원본 PDF    [찾기]   │                              │
│  ② 저장 폴더   [변경]   │                              │
│  ③ 파일명 설정          │                              │
│     학년반 | 번호 | 접미어│                              │
│  ④ 페이지 수            │       ◀  1 / 24  ▶          │
│                        │                              │
│  [ ▶ 일괄 분할 시작 ]    │                              │
└─────────────────────────────────────────────────────┘
```

---

## 📁 파일명 규칙

```
{학년반}{번호:02d}{접미어}.pdf

예시)
  학년반: 109 / 접미어: _수학  →  10901_수학.pdf, 10902_수학.pdf ...
  학년반: 201 / 접미어: 없음   →  20101.pdf, 20102.pdf ...
```

---

## 🚀 실행 방법

### A. EXE 직접 실행 (배포용, 권장)

```
PDF_Slicer.exe 더블클릭
```

> Python 설치 불필요. Windows 64bit 환경에서 동작합니다.  
> Windows 스마트 앱 컨트롤(SAC)에 걸리는 경우: 파일 우클릭 → 속성 → 차단 해제

### B. Python으로 직접 실행 (개발/수정용)

```bash
# 1. 의존성 설치
pip install customtkinter PyMuPDF Pillow

# 2. 실행
python pdf_slicer.py
```

---

## 🔨 EXE 빌드

```bash
# 빌드_EXE.bat 더블클릭 (자동으로 아래 명령 실행)

pip install pyinstaller
pyinstaller --onefile --windowed --name PDF_Slicer pdf_slicer.py
```

빌드 완료 후 `dist/PDF_Slicer.exe` 파일만 배포하면 됩니다.  
`build/` 폴더는 임시 파일이므로 삭제해도 됩니다.

---

## 📦 의존성

```
customtkinter >= 5.0
PyMuPDF (fitz) >= 1.20
Pillow >= 9.0
Python >= 3.10
```

---

## 🗓️ 개발 히스토리

| 버전 | 내용 |
|---|---|
| v1.0 | tkinter 기반 초기 버전 — 파일 선택, 분할, 저장 기본 기능 |
| v2.0 | CustomTkinter로 UI 전면 리디자인 (다크 사이드바 + 미리보기 패널) |
| v2.1 | 접미어 입력 필드 추가, 파일명 실시간 미리보기 |
| v2.2 | 경로 입력란 우측 정렬(`xview_moveto`) 적용 |
| v2.3 | 분할 완료 후 저장 폴더 자동 열기(`os.startfile`) |
| v2.4 | PyInstaller 빌드 스크립트(`빌드_EXE.bat`) 추가 |

---

## 👨‍🏫 만든 이

경기도 미사강변고등학교 · 정보/AI 교사  
GitHub: [@skywind99](https://github.com/skywind99)

---

## 📄 라이선스

MIT License
