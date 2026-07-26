import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    import fitz  # PyMuPDF
    from PIL import Image, ImageTk
except ImportError as e:
    print(f"라이브러리 설치 필요: {e}")
    print("pip install customtkinter PyMuPDF Pillow")
    sys.exit(1)

# ── 테마 설정 ──────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ACCENT   = "#2563EB"   # 파란색 포인트
BG_DARK  = "#1E293B"   # 사이드바 배경
BG_CARD  = "#F8FAFC"   # 카드 배경
TEXT_MAIN= "#0F172A"
TEXT_SUB = "#64748B"
BORDER   = "#E2E8F0"
SUCCESS  = "#10B981"
DANGER   = "#EF4444"


class PDFSlicerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto PDF Slicer")
        self.geometry("1020x680")
        self.minsize(900, 580)
        self.configure(fg_color=BG_CARD)

        # 상태 변수
        self.current_pdf  = ""
        self.current_page = 0
        self.total_pages  = 0
        self._photo_ref   = None

        self._build_ui()

    # ──────────────────────────────────────────────────────────────────────────
    # UI 구성
    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # 루트 2열 배치
        self.grid_columnconfigure(0, weight=0)   # 왼쪽 패널 고정
        self.grid_columnconfigure(1, weight=1)   # 오른쪽 미리보기 확장
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_preview_panel()

    # ── 왼쪽 사이드바 ─────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=390, fg_color=BG_DARK, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(99, weight=1)   # 스페이서 행

        # ── 로고 & 타이틀 ──
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(28, 22))

        ctk.CTkLabel(header, text="✂", font=("Pretendard", 32), text_color=ACCENT).pack(side="left")
        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left", padx=10)
        ctk.CTkLabel(title_col, text="PDF Slicer", font=("Pretendard", 20, "bold"),
                     text_color="#F1F5F9").pack(anchor="w")
        ctk.CTkLabel(title_col, text="스캔 답안지 자동 분할기",
                     font=("Pretendard", 11), text_color="#94A3B8").pack(anchor="w")

        # ── 구분선 ──
        ctk.CTkFrame(sidebar, height=1, fg_color="#334155").grid(
            row=1, column=0, sticky="ew", padx=28, pady=(0, 20))

        row = 2

        # ① 원본 PDF
        ctk.CTkLabel(sidebar, text="① 원본 PDF", font=("Pretendard", 11, "bold"),
                     text_color="#94A3B8").grid(row=row, column=0, sticky="w", padx=28, pady=(0,6))
        row += 1

        file_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        file_row.grid(row=row, column=0, sticky="ew", padx=28)
        file_row.grid_columnconfigure(0, weight=1)
        self.entry_file = ctk.CTkEntry(file_row, placeholder_text="파일을 선택하세요",
                                       height=36, corner_radius=8, fg_color="#334155",
                                       border_color="#475569", text_color="#E2E8F0")
        self.entry_file.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(file_row, text="찾기", width=56, height=36, corner_radius=8,
                      fg_color=ACCENT, hover_color="#1D4ED8",
                      command=self.select_file).grid(row=0, column=1, padx=(6,0))
        row += 1

        # ② 저장 폴더
        ctk.CTkLabel(sidebar, text="② 저장 폴더", font=("Pretendard", 11, "bold"),
                     text_color="#94A3B8").grid(row=row, column=0, sticky="w", padx=28, pady=(18,6))
        row += 1

        dest_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        dest_row.grid(row=row, column=0, sticky="ew", padx=28)
        dest_row.grid_columnconfigure(0, weight=1)
        self.entry_dest = ctk.CTkEntry(dest_row, placeholder_text="자동으로 설정됩니다",
                                       height=36, corner_radius=8, fg_color="#334155",
                                       border_color="#475569", text_color="#E2E8F0",
                                       justify="right")
        self.entry_dest.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(dest_row, text="변경", width=56, height=36, corner_radius=8,
                      fg_color="#475569", hover_color="#64748B",
                      command=self.select_dest_folder).grid(row=0, column=1, padx=(6,0))
        row += 1

        # ③ 파일명 설정
        ctk.CTkLabel(sidebar, text="③ 파일명 설정", font=("Pretendard", 11, "bold"),
                     text_color="#94A3B8").grid(row=row, column=0, sticky="w", padx=28, pady=(18,6))
        row += 1

        fname_card = ctk.CTkFrame(sidebar, fg_color="#0F172A", corner_radius=10)
        fname_card.grid(row=row, column=0, sticky="ew", padx=28)
        fname_card.grid_columnconfigure(0, weight=1)
        fname_card.grid_columnconfigure(1, weight=0)
        fname_card.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(fname_card, text="학년반  ", font=("Pretendard", 10),
                     text_color="#94A3B8").grid(row=0, column=0, sticky="w", padx=14, pady=(10,2))
        ctk.CTkLabel(fname_card, text="번호", font=("Pretendard", 10),
                     text_color="#94A3B8").grid(row=0, column=1, sticky="w", pady=(10,2))
        ctk.CTkLabel(fname_card, text="접미어(선택)", font=("Pretendard", 10),
                     text_color="#94A3B8").grid(row=0, column=2, sticky="w", padx=(8,14), pady=(10,2))

        self.entry_prefix = ctk.CTkEntry(fname_card, placeholder_text="예) 109",
                                         width=90, height=34, corner_radius=6,
                                         fg_color="#1E293B", border_color="#334155",
                                         text_color="#E2E8F0")
        self.entry_prefix.grid(row=1, column=0, sticky="w", padx=14, pady=(0,10))

        ctk.CTkLabel(fname_card, text="01", font=("Pretendard", 13, "bold"),
                     text_color="#475569").grid(row=1, column=1, pady=(0,10))

        self.entry_suffix = ctk.CTkEntry(fname_card, placeholder_text="_수학",
                                         width=95, height=34, corner_radius=6,
                                         fg_color="#1E293B", border_color="#334155",
                                         text_color="#E2E8F0")
        self.entry_suffix.grid(row=1, column=2, padx=(8,14), pady=(0,10))

        row += 1

        # 미리보기 레이블
        self.label_fname_preview = ctk.CTkLabel(
            sidebar, text="예: 10901_수학.pdf",
            font=("Pretendard", 10), text_color="#60A5FA")
        self.label_fname_preview.grid(row=row, column=0, sticky="w", padx=28, pady=(4,0))
        row += 1

        # 실시간 업데이트 바인드
        self.entry_prefix.bind("<KeyRelease>", lambda e: self._update_fname_preview())
        self.entry_suffix.bind("<KeyRelease>", lambda e: self._update_fname_preview())

        # ④ 페이지 간격
        ctk.CTkLabel(sidebar, text="④ 학생 1명당 페이지 수", font=("Pretendard", 11, "bold"),
                     text_color="#94A3B8").grid(row=row, column=0, sticky="w", padx=28, pady=(18,6))
        row += 1

        interval_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        interval_row.grid(row=row, column=0, sticky="ew", padx=28)

        self.entry_interval = ctk.CTkEntry(interval_row, placeholder_text="2",
                                           width=80, height=36, corner_radius=8,
                                           fg_color="#334155", border_color="#475569",
                                           text_color="#E2E8F0")
        self.entry_interval.grid(row=0, column=0)
        ctk.CTkLabel(interval_row, text="쪽", font=("Pretendard", 13),
                     text_color="#94A3B8").grid(row=0, column=1, padx=(8,0))
        row += 1

        # 스페이서
        ctk.CTkLabel(sidebar, text="").grid(row=99, column=0)

        # ── 실행 버튼 ──
        ctk.CTkFrame(sidebar, height=1, fg_color="#334155").grid(
            row=100, column=0, sticky="ew", padx=28, pady=(0,16))

        self.btn_run = ctk.CTkButton(
            sidebar, text="▶  일괄 분할 시작", height=48,
            font=("Pretendard", 14, "bold"),
            fg_color=ACCENT, hover_color="#1D4ED8", corner_radius=10,
            command=self.execute_bulk_slice)
        self.btn_run.grid(row=101, column=0, sticky="ew", padx=28, pady=(0,8))

        # 상태 표시
        self.label_status = ctk.CTkLabel(sidebar, text="", font=("Pretendard", 10),
                                         text_color="#60A5FA")
        self.label_status.grid(row=102, column=0, pady=(0,24))

    # ── 오른쪽 미리보기 패널 ──────────────────────────────────────────────────
    def _build_preview_panel(self):
        panel = ctk.CTkFrame(self, fg_color=BORDER, corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(panel, fg_color=BG_CARD, corner_radius=16)
        inner.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        # 미리보기 캔버스 (스크롤 가능)
        self.canvas = tk.Canvas(inner, bg="#E2E8F0", highlightthickness=0, cursor="hand2")
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20,8))

        # 페이지 없을 때 안내문
        self._draw_placeholder()

        # 하단 네비게이션
        nav = ctk.CTkFrame(inner, fg_color="transparent")
        nav.grid(row=1, column=0, pady=(4, 20))

        self.btn_prev = ctk.CTkButton(nav, text="◀", width=40, height=34,
                                      corner_radius=8, fg_color="#E2E8F0",
                                      text_color=TEXT_MAIN, hover_color="#CBD5E1",
                                      command=self.prev_page)
        self.btn_prev.pack(side="left", padx=4)

        self.label_page = ctk.CTkLabel(nav, text="— / —",
                                       font=("Pretendard", 13, "bold"),
                                       text_color=TEXT_SUB, width=100)
        self.label_page.pack(side="left", padx=8)

        self.btn_next = ctk.CTkButton(nav, text="▶", width=40, height=34,
                                      corner_radius=8, fg_color="#E2E8F0",
                                      text_color=TEXT_MAIN, hover_color="#CBD5E1",
                                      command=self.next_page)
        self.btn_next.pack(side="left", padx=4)

        # 마우스 휠 스크롤
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>",   self._on_mousewheel)
        self.canvas.bind("<Button-5>",   self._on_mousewheel)

        # 캔버스 리사이즈 감지
        self.canvas.bind("<Configure>", lambda e: self._redraw_page())

        self._preview_inner = inner

    def _draw_placeholder(self):
        self.canvas.delete("all")
        self.canvas.after(10, self._center_placeholder)

    def _center_placeholder(self):
        w = self.canvas.winfo_width() or 400
        h = self.canvas.winfo_height() or 500
        self.canvas.create_text(w//2, h//2 - 16, text="📄",
                                font=("Arial", 48), fill="#CBD5E1", tags="ph")
        self.canvas.create_text(w//2, h//2 + 36, text="PDF 파일을 선택하면\n미리보기가 표시됩니다.",
                                font=("Pretendard", 13), fill="#94A3B8",
                                justify="center", tags="ph")

    # ──────────────────────────────────────────────────────────────────────────
    # 파일명 미리보기 업데이트
    # ──────────────────────────────────────────────────────────────────────────
    def _update_fname_preview(self):
        prefix = self.entry_prefix.get().strip() or "101"
        suffix = self.entry_suffix.get().strip()
        self.label_fname_preview.configure(text=f"예: {prefix}01{suffix}.pdf")

    # ──────────────────────────────────────────────────────────────────────────
    # 파일/폴더 선택
    # ──────────────────────────────────────────────────────────────────────────
    def select_file(self):
        fp = filedialog.askopenfilename(
            title="스캔한 원본 PDF 선택", filetypes=[("PDF Files", "*.pdf")])
        if not fp:
            return
        self.entry_file.delete(0, "end")
        self.entry_file.insert(0, fp)
        self.entry_file.xview_moveto(1.0)
        self.current_pdf  = fp
        self.current_page = 0

        base = os.path.dirname(fp)
        default_dest = os.path.join(base, "분할완료")
        self.entry_dest.delete(0, "end")
        self.entry_dest.insert(0, default_dest)
        self.entry_dest.xview_moveto(1.0)

        self._update_fname_preview()
        self.update_preview()

    def select_dest_folder(self):
        cur = self.entry_dest.get().strip()
        initial = os.path.dirname(cur) if cur else "/"
        fp = filedialog.askdirectory(title="저장 폴더 선택", initialdir=initial)
        if fp:
            self.entry_dest.delete(0, "end")
            self.entry_dest.insert(0, fp)
            self.entry_dest.xview_moveto(1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # PDF 미리보기
    # ──────────────────────────────────────────────────────────────────────────
    def update_preview(self):
        if not self.current_pdf or not os.path.isfile(self.current_pdf):
            return
        threading.Thread(target=self._load_page_thread, daemon=True).start()

    def _load_page_thread(self):
        try:
            doc = fitz.open(self.current_pdf)
            self.total_pages = len(doc)
            if self.current_page < 0: self.current_page = 0
            if self.current_page >= self.total_pages: self.current_page = self.total_pages - 1

            page = doc.load_page(self.current_page)

            # 캔버스 크기에 맞춰 zoom
            cw = max(self.canvas.winfo_width(), 300)
            ch = max(self.canvas.winfo_height(), 400)
            rect = page.rect
            zoom = min((cw - 32) / rect.width, (ch - 32) / rect.height) * 2  # 고해상도
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self._pending_img = img
            doc.close()

            self.after(0, self._display_page_image)
        except Exception as e:
            self.after(0, lambda: self.label_status.configure(
                text=f"미리보기 오류: {e}", text_color=DANGER))

    def _display_page_image(self):
        if not hasattr(self, "_pending_img"):
            return
        img = self._pending_img

        # 캔버스 크기에 맞게 스케일 다운 (표시용)
        cw = max(self.canvas.winfo_width(), 300)
        ch = max(self.canvas.winfo_height(), 400)
        img.thumbnail((cw - 24, ch - 24), Image.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        self._photo_ref = photo

        self.canvas.delete("all")
        cx, cy = cw // 2, ch // 2
        # 그림자 효과
        self.canvas.create_rectangle(cx - img.width//2 + 4, cy - img.height//2 + 4,
                                     cx + img.width//2 + 4, cy + img.height//2 + 4,
                                     fill="#CBD5E1", outline="")
        self.canvas.create_image(cx, cy, image=photo)

        self.label_page.configure(
            text=f"{self.current_page + 1}  /  {self.total_pages}")

    def _redraw_page(self):
        if self.current_pdf and os.path.isfile(self.current_pdf):
            self.update_preview()
        else:
            self._draw_placeholder()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_preview()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_preview()

    def _on_mousewheel(self, event):
        delta = getattr(event, "delta", 0)
        if event.num == 4 or delta > 0:
            self.prev_page()
        elif event.num == 5 or delta < 0:
            self.next_page()

    # ──────────────────────────────────────────────────────────────────────────
    # 핵심 로직: 일괄 분할
    # ──────────────────────────────────────────────────────────────────────────
    def execute_bulk_slice(self):
        input_pdf    = self.entry_file.get().strip()
        dest_folder  = self.entry_dest.get().strip()
        prefix       = self.entry_prefix.get().strip()
        suffix       = self.entry_suffix.get().strip()
        interval_str = self.entry_interval.get().strip()

        if not os.path.isfile(input_pdf):
            messagebox.showerror("오류", "스캔한 원본 PDF 파일을 먼저 선택하세요.")
            return
        if not prefix:
            messagebox.showerror("오류", "학년/반 앞자리를 입력하세요. (예: 109)")
            return
        if not interval_str.isdigit() or int(interval_str) < 1:
            messagebox.showerror("오류", "학생 1명당 페이지 수(간격)를 숫자로 입력하세요.")
            return

        interval = int(interval_str)

        if not os.path.exists(dest_folder):
            try:
                os.makedirs(dest_folder)
            except Exception as e:
                messagebox.showerror("오류", f"저장 폴더를 생성할 수 없습니다:\n{e}")
                return

        self.btn_run.configure(state="disabled", text="처리 중…")
        self.label_status.configure(text="분할 중입니다…", text_color="#60A5FA")

        threading.Thread(target=self._slice_thread,
                         args=(input_pdf, dest_folder, prefix, suffix, interval),
                         daemon=True).start()

    def _slice_thread(self, input_pdf, dest_folder, prefix, suffix, interval):
        try:
            doc_original = fitz.open(input_pdf)
            total_p = len(doc_original)
            saved = 0

            for i, start_idx in enumerate(range(0, total_p, interval)):
                end_idx = min(start_idx + interval - 1, total_p - 1)
                student_num = i + 1

                doc_new = fitz.open()
                doc_new.insert_pdf(doc_original, from_page=start_idx, to_page=end_idx)

                filename = f"{prefix}{student_num:02d}{suffix}.pdf"
                doc_new.save(os.path.join(dest_folder, filename))
                doc_new.close()
                saved += 1

                self.after(0, lambda s=saved, tot=total_p//interval: self.label_status.configure(
                    text=f"진행: {s} / {tot}", text_color="#60A5FA"))

            doc_original.close()
            self.after(0, self._on_slice_done, saved, dest_folder)

        except Exception as e:
            self.after(0, lambda: [
                self.label_status.configure(text=f"오류: {e}", text_color=DANGER),
                self.btn_run.configure(state="normal", text="▶  일괄 분할 시작"),
                messagebox.showerror("오류", f"작업 중 문제 발생:\n{e}")
            ])

    def _on_slice_done(self, saved, dest_folder):
        self.btn_run.configure(state="normal", text="▶  일괄 분할 시작")
        self.label_status.configure(text=f"✓ {saved}명 파일 완성!", text_color=SUCCESS)
        messagebox.showinfo("완료",
            f"✅ {saved}명의 파일로 분할 완료!\n\n📁 저장 위치:\n{dest_folder}")
        os.startfile(dest_folder)


if __name__ == "__main__":
    app = PDFSlicerApp()
    app.mainloop()
