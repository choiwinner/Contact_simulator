import tkinter as tk
from tkinter import ttk
import math

# 다이얼 조정식 소켓 접촉 시뮬레이터 (Dial Version)
# 이 파일은 사용자의 요청에 따라 새롭게 설계 및 작성된 파일입니다.
# Heatsink, Insert, Socket Guide가 통합되어 Dial과 Dial Offset으로 내부 공간을 조절하는 방식입니다.

class DialSocketSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dial-Adjusted Socket Contact Simulator")
        self.root.geometry("1280x760")
        self.root.resizable(False, False)
        
        self.SCALE = 25
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # 좌측 제어 패널 설정
        left_panel = ttk.Frame(root, padding=15, width=420, relief="groove")
        left_panel.pack(side="left", fill="y", expand=False)
        left_panel.pack_propagate(False)
        
        # 우측 시각화 패널 설정
        right_panel = ttk.Frame(root, padding=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # 타이틀
        title_label = tk.Label(left_panel, text="다이얼식 소켓 접촉 시뮬레이터", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # -------------------------------------------------------------
        # [레시피 선택 (Recipes) 구역 추가]
        # -------------------------------------------------------------
        recipe_group = ttk.LabelFrame(left_panel, text=" 레시피 선택 (Recipes) ", padding=10)
        recipe_group.pack(fill="x", pady=5)
        
        # 2열 균등 배치 설정
        for col in range(2):
            recipe_group.columnconfigure(col, weight=1, uniform="recipe_col")
            
        # 1. Rubber Socket (활성화 및 HBM 규격 연동)
        lbl_rubber = tk.Label(recipe_group, text="Rubber Socket", font=("Helvetica", 9, "bold"))
        lbl_rubber.grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        self.combo_rubber = ttk.Combobox(recipe_group, values=["사용자 입력", "HBM3E", "HBM4", "HBM4E"], state="readonly")
        self.combo_rubber.set("사용자 입력")
        self.combo_rubber.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.combo_rubber.bind("<<ComboboxSelected>>", self.on_recipe_changed)
        
        # 2. Dial Offset (활성화 및 Latch 규격 연동)
        lbl_offset = tk.Label(recipe_group, text="Dial Offset", font=("Helvetica", 9, "bold"))
        lbl_offset.grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))
        self.combo_offset = ttk.Combobox(recipe_group, values=["사용자 입력", "HBM3E Latch", "HBM4 Latch"], state="readonly")
        self.combo_offset.set("사용자 입력")
        self.combo_offset.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 5))
        self.combo_offset.bind("<<ComboboxSelected>>", self.on_offset_recipe_changed)
        
        # -------------------------------------------------------------
        # [입력 파라미터 구역]
        # -------------------------------------------------------------
        input_group = ttk.LabelFrame(left_panel, text=" 입력 파라미터 (Inputs) ", padding=10)
        input_group.pack(fill="x", pady=5)
        
        self.vars = {
            "s_max": tk.DoubleVar(value=0.55),
            "s_hard": tk.DoubleVar(value=0.4),
            "d_h": tk.DoubleVar(value=10.0),
            "dial_val": tk.DoubleVar(value=10.4),
            "dial_offset": tk.DoubleVar(value=0.4)
        }
        self.slider_labels = {}
        self.sliders = {}
        
        self.create_slider(input_group, "Socket 최대 높이 (S_max)", "s_max", 0.1, 1.5)
        self.create_slider(input_group, "Socket Hard Stop (S_hard)", "s_hard", 0.2, 1.3)
        self.create_slider(input_group, "Device 높이 (D_h)", "d_h", 8.0, 12.0)
        self.create_slider(input_group, "Dial 값 (Dial)", "dial_val", 8.0, 11.0)
        self.create_slider(input_group, "Dial Offset (Offset)", "dial_offset", 0.0, 2.0)
        
        # -------------------------------------------------------------
        # [연산 결과 구역]
        # -------------------------------------------------------------
        output_group = ttk.LabelFrame(left_panel, text=" 연산 결과 (Outputs) ", padding=10)
        output_group.pack(fill="x", pady=10)
        
        self.res_space = tk.Label(output_group, text="실제 내부 공간 (Space): 0.00 mm", font=("Helvetica", 10, "bold"), fg="#0D47A1")
        self.res_space.pack(anchor="w", pady=2)
        
        self.res_val1 = tk.Label(output_group, text="1) Hard Stop + Device (최소 허용치): 0.00 mm", font=("Helvetica", 10))
        self.res_val1.pack(anchor="w", pady=2)
        
        self.res_status = tk.Label(output_group, text="결과: Pass", font=("Helvetica", 13, "bold"), fg="green")
        self.res_status.pack(anchor="w", pady=10)
        
        self.res_compression = tk.Label(output_group, text="Socket 압축 길이: 0.00 mm", font=("Helvetica", 10))
        self.res_compression.pack(anchor="w", pady=2)
        
        self.res_gap = tk.Label(output_group, text="", font=("Helvetica", 10))
        self.res_gap.pack(anchor="w", pady=2)
        
        # 💡 장비 구조 설명 정보 추가
        info_txt = "💡 장비 구조 설명:\n" \
                   "- PCB 위에 소켓(Socket)과 디바이스(Device)가 놓입니다.\n" \
                   "- 상단 뚜껑(Lid) 프레임이 닫혀서 베이스에 고정됩니다.\n" \
                   "- Lid 상단의 다이얼(Dial)을 조여 Pusher가 상하 이송됩니다.\n" \
                   "- Dial 값 + Dial Offset 값이 실제 하우징 내부 공간 높이가 됩니다."
        tk.Label(left_panel, text=info_txt, font=("Helvetica", 9), fg="#555555", justify="left").pack(side="bottom", fill="x", pady=10)
        
        # 캔버스 시각화 구역
        self.canvas = tk.Canvas(right_panel, bg="#ECEFF1", highlightthickness=1, highlightbackground="#CFD8DC")
        self.canvas.pack(fill="both", expand=True)
        
        # 리사이즈 핸들러 바인딩
        self.canvas.bind("<Configure>", lambda e: self.update_simulation())
        
        self.update_simulation()

    def create_slider(self, parent, text, var_name, from_, to_):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        lbl = tk.Label(frame, text=text, font=("Helvetica", 9), width=25, anchor="w")
        lbl.pack(side="left")
        val_lbl = tk.Label(frame, text="", font=("Helvetica", 9, "bold"), fg="#1976D2", width=5, anchor="e")
        val_lbl.pack(side="right")
        var = self.vars[var_name]
        
        scale = ttk.Scale(frame, from_=from_, to=to_, variable=var, command=lambda e: self.update_simulation())
        scale.pack(side="right", fill="x", expand=True, padx=5)
        
        self.sliders[var_name] = scale
        self.slider_labels[var_name] = val_lbl

    def on_recipe_changed(self, event):
        recipe = self.combo_rubber.get()
        if recipe == "HBM3E":
            self.vars["s_max"].set(0.55)
            self.vars["s_hard"].set(0.40)
            self.sliders["s_max"].config(state="disabled")
            self.sliders["s_hard"].config(state="disabled")
        elif recipe == "HBM4":
            self.vars["s_max"].set(0.75)
            self.vars["s_hard"].set(0.50)
            self.sliders["s_max"].config(state="disabled")
            self.sliders["s_hard"].config(state="disabled")
        elif recipe == "HBM4E":
            self.vars["s_max"].set(0.55)
            self.vars["s_hard"].set(0.38)
            self.sliders["s_max"].config(state="disabled")
            self.sliders["s_hard"].config(state="disabled")
        else: # 사용자 입력
            self.sliders["s_max"].config(state="normal")
            self.sliders["s_hard"].config(state="normal")
            
        self.update_simulation()

    def on_offset_recipe_changed(self, event):
        offset_recipe = self.combo_offset.get()
        if offset_recipe == "HBM3E Latch":
            self.vars["dial_offset"].set(0.40)
            self.sliders["dial_offset"].config(state="disabled")
        elif offset_recipe == "HBM4 Latch":
            self.vars["dial_offset"].set(0.50)
            self.sliders["dial_offset"].config(state="disabled")
        else: # 사용자 입력
            self.sliders["dial_offset"].config(state="normal")
            
        self.update_simulation()

    def update_simulation(self):
        # 0. 입력값 0.05 단위 스냅 (Snap to 0.05)
        recipe = self.combo_rubber.get()
        offset_recipe = self.combo_offset.get()
        for key, var in self.vars.items():
            if key in ["s_max", "s_hard"] and recipe in ["HBM3E", "HBM4", "HBM4E"]:
                continue
            if key == "dial_offset" and offset_recipe in ["HBM3E Latch", "HBM4 Latch"]:
                continue
            val = var.get()
            stepped_val = round(val * 20.0) / 20.0
            if abs(val - stepped_val) > 1e-6:
                var.set(stepped_val)

        # 1. 입력 파라미터 가져오기
        s_max = self.vars["s_max"].get()
        s_hard = self.vars["s_hard"].get()
        d_h = self.vars["d_h"].get()
        dial_val = self.vars["dial_val"].get()
        dial_offset = self.vars["dial_offset"].get()

        # 라벨 표시 업데이트
        for key, lbl in self.slider_labels.items():
            lbl.config(text=f"{self.vars[key].get():.2f}")
            
        # 2. 물리적 조건 계산
        space = dial_val + dial_offset
        val1 = s_hard + d_h # 최소 필요 공간
        s_initial_stack = s_max + d_h # 미압축 스택
        
        self.res_space.config(text=f"실제 내부 공간 (Space): {space:.2f} mm")
        self.res_val1.config(text=f"1) Hard Stop + Device (최소 허용치): {val1:.2f} mm")
        
        device_crushed = False
        
        if space < val1 - 1e-5:
            status = "Fail (Over-compressed)"
            color = "#D32F2F"
            comp_len = s_max - s_hard
            short_len = val1 - space
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (Hard Stop 도달)")
            self.res_gap.config(text=f"Device 간섭량 (Crushed): {short_len:.2f} mm", fg="#D32F2F")
            
            heatsink_val = space
            socket_val = s_hard
            device_crushed = True
            
        elif space >= s_initial_stack - 1e-5:
            status = "Fail (No Contact)"
            color = "#F57C00"
            comp_len = 0.0
            short_len = space - s_initial_stack
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (미압축)")
            self.res_gap.config(text=f"모자른 길이 (Gap): {short_len:.2f} mm", fg="#F57C00")
            
            heatsink_val = space
            socket_val = s_max
            
        elif abs(val1 - space) < 1e-5:
            status = "Pass"
            color = "#388E3C"
            comp_len = s_initial_stack - space
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
            self.res_gap.config(text="")
            
            heatsink_val = space
            socket_val = space - d_h
            
        else:
            remaining = space - val1
            status = f"조건부 Pass ({remaining:.2f}mm 부족)"
            color = "#F9A825"
            comp_len = s_initial_stack - space
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
            self.res_gap.config(text="")
            
            heatsink_val = space
            socket_val = space - d_h

        # 3. Canvas 그리기
        self.canvas.delete("all")
        
        cx = self.canvas.winfo_width() / 2
        if cx < 100: cx = 400  # 기본 중앙 좌표
        base_y = self.canvas.winfo_height() - 80
        if base_y < 100: base_y = 580
        
        SCALE = self.SCALE
        
        # --- [1. PCB 바닥판] ---
        self.canvas.create_rectangle(cx-360, base_y, cx+360, base_y+35, fill="#1B5E20", outline="#0D3F12", width=2)
        self.canvas.create_text(cx, base_y+17, text="PCB", fill="white", font=("Helvetica", 11, "bold"))
        
        # --- [2. Socket (골드/옐로우)] ---
        soc_w = 200
        p_soc_top = base_y - socket_val * SCALE
        self.canvas.create_rectangle(cx - soc_w/2, p_soc_top, cx + soc_w/2, base_y, fill="#FFCA28", outline="#FF8F00", width=2)
        self.canvas.create_text(cx, (p_soc_top + base_y)/2, text="Socket", fill="#5D4037", font=("Helvetica", 10, "bold"))
        
        # --- [3. Device (블루/레드)] ---
        dev_w = 220
        p_dev_bottom = p_soc_top
        if device_crushed:
            p_dev_top = base_y - heatsink_val * SCALE
            self.canvas.create_rectangle(cx - dev_w/2, p_dev_top, cx + dev_w/2, p_dev_bottom, fill="#E53935", outline="#B71C1C", width=2)
            self.canvas.create_text(cx, (p_dev_top + p_dev_bottom)/2, text="DEVICE CRUSHED", fill="white", font=("Helvetica", 10, "bold"))
        else:
            p_dev_top = p_dev_bottom - d_h * SCALE
            self.canvas.create_rectangle(cx - dev_w/2, p_dev_top, cx + dev_w/2, p_dev_bottom, fill="#2196F3", outline="#0D47A1", width=2)
            self.canvas.create_text(cx, (p_dev_top + p_dev_bottom)/2, text="Device", fill="white", font=("Helvetica", 10, "bold"))
            
        # --- [4. 상단 Lid 구조물 (실버 금속 재질, 디바이스와 소켓을 감싸는 단순 ㄷ자 구조)] ---
        lid_top_y = base_y - 13.5 * SCALE  # 뚜껑 프레임 자체의 상단면 고정
        lid_leg_bot = base_y  # PCB 상면까지 ㄷ자 다리가 완전히 내려옴
        
        # 4-1) ㄷ자 형태의 금속 Lid 프레임 (Device와 Socket을 양옆에서 뭉텅이로 감싸는 수직 구조)
        # 내벽: cx ± 130, 외벽: cx ± 155
        lid_points = [
            cx - 155, lid_leg_bot,          # 좌측 외벽 하단 (PCB 밀착)
            cx - 155, lid_top_y,            # 좌측 외벽 상단
            cx + 155, lid_top_y,            # 우측 외벽 상단
            cx + 155, lid_leg_bot,          # 우측 외벽 하단 (PCB 밀착)
            cx + 130, lid_leg_bot,          # 우측 내벽 하단 (PCB 밀착)
            cx + 130, lid_top_y + 30,        # 우측 내벽 상단 (천장 아래)
            cx - 130, lid_top_y + 30,        # 좌측 내벽 상단 (천장 아래)
            cx - 130, lid_leg_bot            # 좌측 내벽 하단 (PCB 밀착)
        ]
        self.canvas.create_polygon(lid_points, fill="#CFD8DC", outline="#78909C", width=2)
        
        # --- [6. Pusher (다이얼로 움직이는 실버 블록)] ---
        hs_w = 215
        p_hs_bottom = base_y - heatsink_val * SCALE
        p_hs_top = p_hs_bottom - 1.8 * SCALE
        
        self.canvas.create_rectangle(cx - hs_w/2, p_hs_top, cx + hs_w/2, p_hs_bottom, fill="#CFD8DC", outline="#78909C", width=2)
        # 푸셔 세로 빗금선 묘사
        for step in range(-7, 8):
            line_x = cx + step * 14
            self.canvas.create_line(line_x, p_hs_top + 5, line_x, p_hs_bottom - 5, fill="#B0BEC5", width=1)
        self.canvas.create_text(cx, (p_hs_top + p_hs_bottom)/2, text="Pusher", fill="#37474F", font=("Helvetica", 9, "bold"))
        
        # --- [7. 다이얼 (Dial Knob) & 나사축] ---
        # 나사축 (Lid와 Pusher 사이를 연결)
        shaft_top_y = lid_top_y - 15
        self.canvas.create_rectangle(cx - 12, shaft_top_y, cx + 12, p_hs_top, fill="#B0BEC5", outline="#455A64", width=1.5)
        # 나사산 라인들
        for sy in range(int(shaft_top_y) + 5, int(p_hs_top) - 5, 6):
            self.canvas.create_line(cx - 12, sy, cx + 12, sy + 3, fill="#455A64", width=1)
            
        # 다이얼 회전 노브 (Lid 프레임 상단 중앙에 위치)
        dial_knob_h = 35
        dial_knob_w = 80
        dk_top = lid_top_y - dial_knob_h
        
        # 금속 널링(Knurling) 그립 표현을 위해 세로선들을 촘촘히 긋기
        self.canvas.create_rectangle(cx - dial_knob_w/2, dk_top, cx + dial_knob_w/2, lid_top_y, fill="#ECEFF1", outline="#607D8B", width=2)
        for i in range(-5, 6):
            lx = cx + i * 7
            self.canvas.create_line(lx, dk_top + 2, lx, lid_top_y - 2, fill="#B0BEC5", width=2)
            
        # 다이얼의 지시용 돌출 바
        self.canvas.create_rectangle(cx - 25, dk_top - 12, cx + 25, dk_top, fill="#F57C00", outline="#E65100", width=1.5)
        self.canvas.create_text(cx, dk_top - 6, text="DIAL", fill="white", font=("Helvetica", 8, "bold"))
        
        # --- [8. 동적 다이얼 수치 게이지 (Canvas 빈 공간에 표출)] ---
        gx = cx - 310
        gy = 120
        # 게이지 외곽 금속 베젤
        self.canvas.create_oval(gx - 49, gy - 49, gx + 49, gy + 49, fill="", outline="#90A4AE", width=4)
        # 게이지 원형 판
        self.canvas.create_oval(gx - 45, gy - 45, gx + 45, gy + 45, fill="#F5F5F7", outline="#78909C", width=2)
        
        # 게이지 눈금선 그리기
        for angle_deg in range(0, 360, 30):
            rad = math.radians(angle_deg)
            x1 = gx + 37 * math.cos(rad)
            y1 = gy + 37 * math.sin(rad)
            x2 = gx + 43 * math.cos(rad)
            y2 = gy + 43 * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill="#546E7A", width=1)
            
        # 다이얼 값에 비례한 바늘 회전 각도 계산
        # 범위: 8.0 ~ 11.0 mm (총 3.0mm 구간)
        # 바늘 각도는 12시 방향(-90도)에서 출발하여 회전
        gauge_angle = -90 + ((dial_val - 8.0) / (11.0 - 8.0)) * 360
        grad_angle = math.radians(gauge_angle)
        bx = gx + 33 * math.cos(grad_angle)
        by = gy + 33 * math.sin(grad_angle)
        
        # 지침 바늘 (빨간색)
        self.canvas.create_line(gx, gy, bx, by, fill="#D32F2F", width=2, arrow=tk.LAST)
        # 센터 피벗 캡
        self.canvas.create_oval(gx - 4, gy - 4, gx + 4, gy + 4, fill="#37474F", outline="#212121", width=1)
        
        # 디지털 수치 및 라벨 텍스트 표출
        self.canvas.create_text(gx, gy - 24, text="DIAL GAUGE", fill="#78909C", font=("Helvetica", 8, "bold"))
        self.canvas.create_text(gx, gy + 24, text=f"{dial_val:.2f} mm", fill="#263238", font=("Helvetica", 10, "bold"))
        
        # 갭 또는 크러시 화살표 및 수치 시각화
        if device_crushed:
            intended_top = p_dev_bottom - d_h * SCALE
            self.canvas.create_line(cx + 175, intended_top, cx + 175, p_dev_top, fill="red", width=2, arrow=tk.BOTH)
            self.canvas.create_text(cx + 182, (intended_top + p_dev_top)/2, text=f"Crushed {short_len:.2f}mm", fill="red", font=("Helvetica", 9, "bold"), anchor="w")
        elif space >= s_initial_stack - 1e-5:
            # 갭 발생선
            self.canvas.create_line(cx, p_dev_top, cx, p_hs_bottom, fill="#F57C00", width=2, arrow=tk.BOTH)
            self.canvas.create_text(cx + 10, (p_dev_top + p_hs_bottom)/2, text=f"Gap {short_len:.2f}mm", fill="#F57C00", font=("Helvetica", 9, "bold"), anchor="w")

        # --- [참조선 그리기] ---
        # 1) 최소 허용치 라인 (Limit)
        limit_y = base_y - val1 * SCALE
        self.canvas.create_line(cx - 350, limit_y, cx + 350, limit_y, fill="#D32F2F", dash=(4, 2))
        self.canvas.create_text(cx - 350, limit_y - 10, text=f"Limit (Hard Stop+Device): {val1:.2f} mm", fill="#D32F2F", font=("Helvetica", 9, "bold"), anchor="w")
        
        # 2) 실제 내부 공간 라인 (Space)
        space_y = base_y - space * SCALE
        self.canvas.create_line(cx - 350, space_y, cx + 350, space_y, fill="#0D47A1", dash=(4, 2))
        self.canvas.create_text(cx + 350, space_y - 10, text=f"Space (Dial+Offset): {space:.2f} mm", fill="#0D47A1", font=("Helvetica", 9, "bold"), anchor="e")

        # --- [우측 상단 범례 (Legend) 그리기] ---
        c_width = self.canvas.winfo_width()
        if c_width < 100: c_width = 800
        
        legend_x = c_width - 290
        legend_y = 20
        legend_w = 270
        legend_h = 170
        
        # 범례 배경 박스
        self.canvas.create_rectangle(legend_x, legend_y, legend_x + legend_w, legend_y + legend_h, fill="#FFFFFF", outline="#CFD8DC", width=1.5)
        self.canvas.create_text(legend_x + 15, legend_y + 15, text="💡 다이얼식 소켓 범례", font=("Helvetica", 10, "bold"), fill="#333333", anchor="w")
        
        items = [
            ("#1B5E20", "PCB (바닥 인쇄회로기판)"),
            ("#FFCA28", "Socket (소켓 커넥터 핀)"),
            ("#2196F3", "Device (테스트 대상 IC 칩)"),
            ("#CFD8DC", "Pusher (디바이스 가압 블록)")
        ]
        
        curr_y = legend_y + 40
        for color, desc in items:
            self.canvas.create_rectangle(legend_x + 15, curr_y - 6, legend_x + 27, curr_y + 6, fill=color, outline="#666666")
            self.canvas.create_text(legend_x + 35, curr_y, text=desc, font=("Helvetica", 9), fill="#555555", anchor="w")
            curr_y += 20
            
        self.canvas.create_line(legend_x + 10, curr_y + 5, legend_x + legend_w - 10, curr_y + 5, fill="#ECEFF1")
        self.canvas.create_text(legend_x + 15, curr_y + 20, text="내부 공간(Space) = Dial + Dial Offset", font=("Helvetica", 8, "bold"), fill="#E65100", anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = DialSocketSimulationApp(root)
    root.mainloop()
