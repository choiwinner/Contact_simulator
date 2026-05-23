import tkinter as tk
from tkinter import ttk

# 메모리 러버 소켓 접촉 시뮬레이터 - 레시피 선택 기능 추가 버전
# 이 파일은 기존 socket_sim.py를 보존하고 새롭게 생성된 파일입니다.

class SocketSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Rubber Socket Contact Simulator (Recipe Version)")
        self.root.geometry("1280x760") # 레시피 구역이 늘어나 높이를 약간 조정합니다.
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
        title_label = tk.Label(left_panel, text="소켓 접촉 구조 시뮬레이터", font=("Helvetica", 16, "bold"))
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
        
        # 2. PCB Type (준비 중)
        lbl_pcb = tk.Label(recipe_group, text="PCB Type", font=("Helvetica", 9), fg="gray")
        lbl_pcb.grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))
        self.combo_pcb = ttk.Combobox(recipe_group, values=["선택 안 함"], state="disabled")
        self.combo_pcb.set("선택 안 함")
        self.combo_pcb.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 5))
        
        # 3. Guide Type (준비 중)
        lbl_guide = tk.Label(recipe_group, text="Guide Type", font=("Helvetica", 9), fg="gray")
        lbl_guide.grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        self.combo_guide = ttk.Combobox(recipe_group, values=["선택 안 함"], state="disabled")
        self.combo_guide.set("선택 안 함")
        self.combo_guide.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # 4. Insert Type (준비 중)
        lbl_insert = tk.Label(recipe_group, text="Insert Type", font=("Helvetica", 9), fg="gray")
        lbl_insert.grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))
        self.combo_insert = ttk.Combobox(recipe_group, values=["선택 안 함"], state="disabled")
        self.combo_insert.set("선택 안 함")
        self.combo_insert.grid(row=3, column=1, sticky="ew", padx=5, pady=(0, 5))
        
        # 5. Heat Sink Type (준비 중)
        lbl_heatsink = tk.Label(recipe_group, text="Heat Sink Type", font=("Helvetica", 9), fg="gray")
        lbl_heatsink.grid(row=4, column=0, sticky="w", padx=5, pady=(2, 0))
        self.combo_heatsink = ttk.Combobox(recipe_group, values=["선택 안 함"], state="disabled")
        self.combo_heatsink.set("선택 안 함")
        self.combo_heatsink.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # -------------------------------------------------------------
        # [입력 파라미터 구역]
        # -------------------------------------------------------------
        input_group = ttk.LabelFrame(left_panel, text=" 입력 파라미터 (Inputs) ", padding=10)
        input_group.pack(fill="x", pady=5)
        
        self.vars = {
            "s_max": tk.DoubleVar(value=0.55),
            "s_hard": tk.DoubleVar(value=0.4),
            "d_h": tk.DoubleVar(value=10.0),
            "g_h": tk.DoubleVar(value=4.5),
            "i_h": tk.DoubleVar(value=5.0),
            "h_g": tk.DoubleVar(value=0.9)
        }
        self.slider_labels = {}
        self.sliders = {}  # 슬라이더 활성화/비활성화 상태 제어용
        
        self.create_slider(input_group, "Socket 최대 높이 (S_max)", "s_max", 0.1, 1.5)
        self.create_slider(input_group, "Socket Hard Stop (S_hard)", "s_hard", 0.2, 1.3)
        self.create_slider(input_group, "Device 높이 (D_h)", "d_h", 8.0, 12.0)
        self.create_slider(input_group, "Socket Guide 높이 (G_h)", "g_h", 3.0, 6.0)
        self.create_slider(input_group, "Insert 높이 (I_h)", "i_h", 3.0, 6.0)
        self.create_slider(input_group, "Heatsink Device 홈 깊이", "h_g", 0.0, 3.0)
        
        # -------------------------------------------------------------
        # [연산 결과 구역]
        # -------------------------------------------------------------
        output_group = ttk.LabelFrame(left_panel, text=" 연산 결과 (Outputs) ", padding=10)
        output_group.pack(fill="x", pady=10)
        
        self.res_val1 = tk.Label(output_group, text="1) Hard Stop + Device: 0.00 mm", font=("Helvetica", 10))
        self.res_val1.pack(anchor="w", pady=2)
        
        self.res_val2 = tk.Label(output_group, text="2) Guide + Insert + Groove: 0.00 mm", font=("Helvetica", 10))
        self.res_val2.pack(anchor="w", pady=2)
        
        self.res_status = tk.Label(output_group, text="결과: Pass", font=("Helvetica", 13, "bold"), fg="green")
        self.res_status.pack(anchor="w", pady=10)
        
        self.res_compression = tk.Label(output_group, text="Socket 압축 길이: 0.00 mm", font=("Helvetica", 10))
        self.res_compression.pack(anchor="w", pady=2)
        
        self.res_gap = tk.Label(output_group, text="", font=("Helvetica", 10))
        self.res_gap.pack(anchor="w", pady=2)
        

        
        # 캔버스 시각화 구역
        self.canvas = tk.Canvas(right_panel, bg="#F5F5F7", highlightthickness=1, highlightbackground="#D1D1D6")
        self.canvas.pack(fill="both", expand=True)
        
        # 리사이즈 핸들러 바인딩
        self.canvas.bind("<Configure>", lambda e: self.update_simulation())
        
        self.update_simulation()

    def create_slider(self, parent, text, var_name, from_, to_):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        lbl = tk.Label(frame, text=text, font=("Helvetica", 9), width=23, anchor="w")
        lbl.pack(side="left")
        val_lbl = tk.Label(frame, text="", font=("Helvetica", 9, "bold"), fg="#1976D2", width=5, anchor="e")
        val_lbl.pack(side="right")
        var = self.vars[var_name]
        
        # 슬라이더 생성 후 self.sliders에 보관하여 차후 활성/비활성 처리
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

    def update_simulation(self):
        # 0. 입력값 0.05 단위 스냅 (Snap to 0.05)
        # 단, '사용자 입력'이 아닌 고정 레시피 모드일 때는 s_max, s_hard에 스냅을 적용하지 않습니다.
        is_user_mode = (self.combo_rubber.get() == "사용자 입력")
        for key, var in self.vars.items():
            if key in ["s_max", "s_hard"] and not is_user_mode:
                continue
            val = var.get()
            stepped_val = round(val * 20.0) / 20.0
            if abs(val - stepped_val) > 1e-6:
                var.set(stepped_val)

        # 1. 입력 파라미터 가져오기
        s_max = self.vars["s_max"].get()
        s_hard = self.vars["s_hard"].get()
        d_h = self.vars["d_h"].get()
        g_h = self.vars["g_h"].get()
        i_h = self.vars["i_h"].get()
        h_g = self.vars["h_g"].get()

        # 라벨 표시 업데이트
        for key, lbl in self.slider_labels.items():
            lbl.config(text=f"{self.vars[key].get():.2f}")
            
        # 2. 물리적 조건 계산
        val1 = s_hard + d_h
        val2 = g_h + i_h + h_g
        s_initial_stack = s_max + d_h
        
        self.res_val1.config(text=f"1) Hard Stop + Device (최소 허용치): {val1:.2f} mm")
        self.res_val2.config(text=f"2) 구조물 압축 목표치 (Val 2): {val2:.2f} mm")
        
        device_crushed = False
        
        if val2 < val1 - 1e-5:
            status = "Fail (Over-compressed)"
            color = "#D32F2F"
            comp_len = s_max - s_hard
            short_len = val1 - val2
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (Hard Stop 도달)")
            self.res_gap.config(text=f"Device 간섭량 (Crushed): {short_len:.2f} mm")
            
            heatsink_val = val2
            socket_val = s_hard
            device_crushed = True
            
        elif val2 >= s_initial_stack - 1e-5:
            status = "Fail (No Contact)"
            color = "#F57C00"
            comp_len = 0.0
            short_len = val2 - s_initial_stack
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (미압축)")
            self.res_gap.config(text=f"모자른 길이 (Gap): {short_len:.2f} mm")
            
            heatsink_val = val2
            socket_val = s_max
            
        elif abs(val1 - val2) < 1e-5:
            status = "Pass"
            color = "#388E3C" # Green
            comp_len = s_initial_stack - val2
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
            self.res_gap.config(text="")
            
            heatsink_val = val2
            socket_val = val2 - d_h
            
        else:
            remaining = val2 - val1
            status = f"조건부 Pass ({remaining:.2f}mm 부족)"
            color = "#F9A825" # Yellow-Orange
            comp_len = s_initial_stack - val2
            self.res_status.config(text=f"결과: {status}", fg=color)
            self.res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
            self.res_gap.config(text="")
            
            heatsink_val = val2
            socket_val = val2 - d_h

        # 3. Canvas 그리기
        self.canvas.delete("all")
        
        cx = self.canvas.winfo_width() / 2
        if cx < 100: cx = 280  # 레이아웃 완료 전 기본값
        base_y = self.canvas.winfo_height() - 50
        if base_y < 100: base_y = 600
        
        SCALE = self.SCALE
        
        # --- [PCB] ---
        self.canvas.create_rectangle(cx-380, base_y, cx+380, base_y+40, fill="#2E7D32", outline="#1B5E20", width=2)
        self.canvas.create_text(cx, base_y+20, text="PCB", fill="white", font=("Helvetica", 11, "bold"))
        
        # --- [Yellow: Socket] ---
        soc_w = 180  # 가로폭 확장 (기존 110에서 180으로)
        p_soc_top = base_y - socket_val * SCALE
        self.canvas.create_rectangle(cx - soc_w/2, p_soc_top, cx + soc_w/2, base_y, fill="#FFCA28", outline="#FF8F00", width=2)
        self.canvas.create_text(cx, (p_soc_top + base_y)/2, text="Socket", fill="#5D4037", font=("Helvetica", 10, "bold"))
        
        # --- [Blue: Device] ---
        dev_w = 210  # 가로폭 확장 (기존 130에서 210으로)
        p_dev_bottom = p_soc_top
        if device_crushed:
            p_dev_top = base_y - heatsink_val * SCALE
            self.canvas.create_rectangle(cx - dev_w/2, p_dev_top, cx + dev_w/2, p_dev_bottom, fill="#E53935", outline="#B71C1C", width=2)
            self.canvas.create_text(cx, (p_dev_top + p_dev_bottom)/2, text="DEVICE CRUSHED", fill="white", font=("Helvetica", 10, "bold"))
        else:
            p_dev_top = p_dev_bottom - d_h * SCALE
            self.canvas.create_rectangle(cx - dev_w/2, p_dev_top, cx + dev_w/2, p_dev_bottom, fill="#42A5F5", outline="#1565C0", width=2)
            self.canvas.create_text(cx, (p_dev_top + p_dev_bottom)/2, text="Device", fill="white", font=("Helvetica", 10, "bold"))
        
        # --- [Black: Socket Guide] ---
        guide_inner = 105  # 가로폭 확장 (기존 65에서 105로, dev_w/2에 맞춤)
        guide_outer = 290  # 가로폭 확장 (기존 185에서 290으로)
        p_guide_top = base_y - g_h * SCALE
        # Left
        self.canvas.create_rectangle(cx - guide_outer, p_guide_top, cx - guide_inner, base_y, fill="#424242", outline="#212121", width=2)
        # Right
        self.canvas.create_rectangle(cx + guide_inner, p_guide_top, cx + guide_outer, base_y, fill="#424242", outline="#212121", width=2)
        # 글자 위치도 가로폭 확장에 맞춰 약간 조정
        self.canvas.create_text(cx - (guide_inner + 230)/2, (p_guide_top + base_y)/2, text="Socket Guide", fill="white", font=("Helvetica", 9))
        self.canvas.create_text(cx + (guide_inner + 230)/2, (p_guide_top + base_y)/2, text="Socket Guide", fill="white", font=("Helvetica", 9))
        
        # --- [Mint: Insert] ---
        insert_inner = 110  # 가로폭 확장 (기존 70에서 110으로, guide_inner보다 약간 넓게)
        insert_outer = 230  # 가로폭 확장 (기존 145에서 230으로, 나사 결합 통로 확보)
        p_insert_bottom = p_guide_top
        p_insert_top = p_insert_bottom - i_h * SCALE
        # Left
        self.canvas.create_rectangle(cx - insert_outer, p_insert_top, cx - insert_inner, p_insert_bottom, fill="#26A69A", outline="#00796B", width=2)
        # Right
        self.canvas.create_rectangle(cx + insert_inner, p_insert_top, cx + insert_outer, p_insert_bottom, fill="#26A69A", outline="#00796B", width=2)
        self.canvas.create_text(cx - (insert_inner+insert_outer)/2, (p_insert_top + p_insert_bottom)/2, text="Insert", fill="white", font=("Helvetica", 9))
        self.canvas.create_text(cx + (insert_inner+insert_outer)/2, (p_insert_top + p_insert_bottom)/2, text="Insert", fill="white", font=("Helvetica", 9))
        
        # --- [Silver: Heat Sink (Side View Style)] ---
        hs_outer = 290  # 가로폭 확장 (기존 185에서 290으로)
        p_hs_groove_top = base_y - heatsink_val * SCALE
        p_hs_rest_bottom = p_hs_groove_top + h_g * SCALE
        
        # 베이스 플레이트 및 하단 연장 다리(Leg) 그리기 (두께를 기존 15에서 45로 증대하여 묵직하게 변경)
        base_h = 45
        p_hs_base_top_center = p_hs_groove_top - base_h
        p_hs_base_top_side = p_hs_rest_bottom - base_h
        
        base_points = [
            cx - hs_outer, p_hs_base_top_side,            # 좌측 바깥 상단
            cx - insert_inner, p_hs_base_top_side,        # 좌측 내측 상단
            cx - insert_inner, p_hs_base_top_center,      # 중앙 홈 좌측 상단
            cx + insert_inner, p_hs_base_top_center,      # 중앙 홈 우측 상단
            cx + insert_inner, p_hs_base_top_side,        # 우측 내측 상단
            cx + hs_outer, p_hs_base_top_side,            # 우측 바깥 상단
            cx + hs_outer, p_guide_top,                    # 우측 바깥 하단 (Socket Guide 상면에 닿음)
            cx + insert_outer, p_guide_top,                # 우측 내측 하단 (Insert 바깥 경계)
            cx + insert_outer, p_hs_rest_bottom,          # 우측 내측 단차 위
            cx + insert_inner, p_hs_rest_bottom,          # 우측 홈 외곽
            cx + insert_inner, p_hs_groove_top,           # 우측 홈 내부 천장
            cx - insert_inner, p_hs_groove_top,           # 좌측 홈 내부 천장
            cx - insert_inner, p_hs_rest_bottom,          # 좌측 홈 외곽
            cx - insert_outer, p_hs_rest_bottom,          # 좌측 내측 단차 위
            cx - insert_outer, p_guide_top,                # 좌측 내측 하단 (Insert 바깥 경계)
            cx - hs_outer, p_guide_top                     # 좌측 바깥 하단 (Socket Guide 상면에 닿음)
        ]
        self.canvas.create_polygon(base_points, fill="#90A4AE", outline="#455A64", width=2)
        
        # 세로 핀(Fins) 그리기 (핀의 상단 높이를 줄여 몸체 두께 대비 핀 길이를 짧게 보이게 함)
        fin_top_y = p_hs_groove_top - 95
        for i in range(23):
            fx = cx - 210 + i * 19.09  # 핀 분포 가로 영역을 420px로 확장 (기존 260px)
            if cx - insert_inner + 5 <= fx <= cx + insert_inner - 5:
                fin_bot_y = p_hs_base_top_center
            else:
                fin_bot_y = p_hs_base_top_side
            
            self.canvas.create_rectangle(
                fx - 2.5, fin_top_y, fx + 2.5, fin_bot_y,
                fill="#CFD8DC", outline="#78909C", width=1
            )
            
        # 가로 핀(Horizontal Fins) 그리기 (Heatsink 좌우 측벽에 돌출)
        side_fin_y_start = p_hs_base_top_side
        side_fin_y_end = p_guide_top
        num_side_fins = 4
        side_fin_len = 60
        side_fin_thick = 8
        
        for i in range(num_side_fins):
            fy = side_fin_y_start + (side_fin_y_end - side_fin_y_start) * (i + 0.5) / num_side_fins
            # 좌측 가로 핀
            self.canvas.create_rectangle(
                cx - hs_outer - side_fin_len, fy - side_fin_thick / 2,
                cx - hs_outer, fy + side_fin_thick / 2,
                fill="#CFD8DC", outline="#78909C", width=1
            )
            # 우측 가로 핀
            self.canvas.create_rectangle(
                cx + hs_outer, fy - side_fin_thick / 2,
                cx + hs_outer + side_fin_len, fy + side_fin_thick / 2,
                fill="#CFD8DC", outline="#78909C", width=1
            )
            
        # 스프링 장착 고정 나사 (Spring-loaded Screws) 그리기 (좌우 2개)
        # 나사는 Insert(폭 230)의 바깥쪽이자 Socket Guide(폭 290) 내부인 cx ± 260 위치에 체결됨
        screw_x_positions = [cx - 260, cx + 260]  # 기존 165에서 260으로 확장
        for sx in screw_x_positions:
            # 나사 샤프트 (Heatsink에서 출발하여 Insert 옆을 관통, Socket Guide 상단 내부까지 길게 연결)
            # 핀 높이 축소에 맞게 나사 머리 높이를 base_top_side 기준 45px로 조절
            shaft_top = p_hs_base_top_side - 45
            shaft_bot = p_guide_top + 12  # Socket Guide 내부로 12px 관통 체결됨
            self.canvas.create_rectangle(
                sx - 3, shaft_top, sx + 3, shaft_bot,
                fill="#B0BEC5", outline="#37474F", width=1.5
            )
            # 나사 머리
            self.canvas.create_rectangle(
                sx - 8, shaft_top - 8, sx + 8, shaft_top,
                fill="#546E7A", outline="#263238", width=1.5
            )
            self.canvas.create_line(sx - 5, shaft_top - 4, sx + 5, shaft_top - 4, fill="#263238", width=1)
            # 스프링 코일 (Heatsink 베이스 플레이트 위쪽에 위치, 스프링 턴 수를 5로 조정)
            spring_top = shaft_top
            spring_bot = p_hs_base_top_side
            turns = 5
            spring_points = []
            for t in range(turns * 2 + 1):
                ty = spring_top + (spring_bot - spring_top) * (t / (turns * 2))
                tx = sx + 8 if t % 2 == 0 else sx - 8
                spring_points.extend([tx, ty])
            self.canvas.create_line(spring_points, fill="#78909C", width=2)
            
            # Socket Guide에 나사가 삽입되는 구멍(Thread hole) 표현
            self.canvas.create_rectangle(
                sx - 5, p_guide_top, sx + 5, p_guide_top + 15,
                fill="#212121", outline="#37474F", width=1
            )
            # 꽂힌 샤프트 부분을 덧그려 체결 상태 묘사
            self.canvas.create_rectangle(
                sx - 2, p_guide_top, sx + 2, shaft_bot,
                fill="#B0BEC5", outline="", width=0
            )
            
        # 히트싱크 라벨 텍스트
        self.canvas.create_text(cx, fin_top_y - 15, text="Heat Sink", fill="#37474F", font=("Helvetica", 11, "bold"))
        
        # --- [참조선 및 갭 마커 그리기] ---
        # 1) Hard Stop 참조선
        val1_y = base_y - val1 * SCALE
        self.canvas.create_line(cx - 320, val1_y, cx + 320, val1_y, fill="red", dash=(4, 2))
        self.canvas.create_text(cx - 320, val1_y - 10, text="1) Hard Stop + Device", fill="red", font=("Helvetica", 9, "bold"), anchor="w")
        
        # 2) 구조물 목표 참조선 (Val 2)
        val2_y = base_y - val2 * SCALE
        self.canvas.create_line(cx - 320, val2_y, cx + 320, val2_y, fill="blue", dash=(4, 2))
        self.canvas.create_text(cx + 320, val2_y - 10, text="2) Structural Close (Val 2)", fill="blue", font=("Helvetica", 9, "bold"), anchor="e")
        
        # 에러 및 갭 표시 화살표 그리기
        if device_crushed:
            intended_top = p_dev_bottom - d_h * SCALE
            mid_x = cx + dev_w/2 + 25
            self.canvas.create_line(mid_x, intended_top, mid_x, p_dev_top, fill="red", width=2, arrow=tk.BOTH)
            self.canvas.create_text(mid_x + 5, (intended_top + p_dev_top)/2, text=f"Crushed {short_len:.2f}mm", fill="red", font=("Helvetica", 8, "bold"), anchor="w")
        elif val2 >= s_initial_stack - 1e-5:
            mid_x = cx
            self.canvas.create_line(mid_x, p_dev_top, mid_x, p_hs_groove_top, fill="orange", width=2, arrow=tk.BOTH)
            self.canvas.create_text(mid_x + 5, (p_dev_top + p_hs_groove_top)/2, text=f"Gap {short_len:.2f}mm", fill="orange", font=("Helvetica", 8, "bold"), anchor="w")

        # --- [우측 상단 범례 (Legend) 그리기] ---
        c_width = self.canvas.winfo_width()
        if c_width < 100:
            c_width = 800  # 레이아웃 완료 전 기본값
            
        legend_x = c_width - 290
        legend_y = 20
        legend_w = 270
        legend_h = 210
        
        # 범례 배경 박스 (둥글거나 깔끔한 사각형)
        self.canvas.create_rectangle(
            legend_x, legend_y, legend_x + legend_w, legend_y + legend_h,
            fill="#FFFFFF", outline="#D1D1D6", width=1.5
        )
        
        # 제목
        self.canvas.create_text(
            legend_x + 15, legend_y + 15,
            text="💡 시뮬레이션 구조 설명",
            font=("Helvetica", 10, "bold"), fill="#333333", anchor="w"
        )
        
        # 각 항목 (색상 사각형 + 설명)
        items = [
            ("#FFCA28", "Yellow: Socket (PCB에 고정)"),
            ("#424242", "Black: Socket Guide (Socket 주변)"),
            ("#42A5F5", "Blue: Device (Socket 위 배치)"),
            ("#26A69A", "Mint: Insert (Guide 위 배치)"),
            ("#90A4AE", "Silver: Heat Sink (모두 덮어 누름)")
        ]
        
        curr_y = legend_y + 45
        for color, desc in items:
            # 색상 표시 박스
            self.canvas.create_rectangle(
                legend_x + 15, curr_y - 6, legend_x + 27, curr_y + 6,
                fill=color, outline="#666666"
            )
            # 텍스트
            self.canvas.create_text(
                legend_x + 35, curr_y,
                text=desc,
                font=("Helvetica", 9), fill="#555555", anchor="w"
            )
            curr_y += 22
            
        # 구분선
        self.canvas.create_line(
            legend_x + 10, curr_y - 2, legend_x + legend_w - 10, curr_y - 2,
            fill="#E5E5EA"
        )
        curr_y += 13
        
        # 조건 텍스트
        self.canvas.create_text(
            legend_x + 15, curr_y,
            text="조건:\n1) <= 2) < (Socket 최대 높이 + Device 높이)",
            font=("Helvetica", 8, "bold"), fill="#E65100", anchor="w", justify="left"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = SocketSimulationApp(root)
    root.mainloop()
