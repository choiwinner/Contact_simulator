import tkinter as tk
from tkinter import ttk
import math

# Latch / HeatSink 통합 소켓 접촉 시뮬레이터 (Total Version)
# 이 파일은 사용자의 요청에 따라 socket_sim_dial.py와 socket_sim_recipe.py를 통합하여 작성된 파일입니다.
# 상단 Latch 및 HeatSink 버튼을 통해 실시간으로 시뮬레이션 모드를 전환할 수 있습니다.

class SocketSimulationTotalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Socket Contact Simulator")
        self.root.geometry("1280x760")
        self.root.resizable(False, False)
        
        self.SCALE = 25
        self.current_mode = "Latch"  # 기본 모드: Latch
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # 좌측 제어 패널 설정
        left_panel = ttk.Frame(root, padding=15, width=420, relief="groove")
        left_panel.pack(side="left", fill="y", expand=False)
        left_panel.pack_propagate(False)
        
        # 우측 시각화 패널 설정
        right_panel = ttk.Frame(root, padding=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # -------------------------------------------------------------
        # [0. 최상단 모드 전환 버튼 구역 (Latch / HeatSink)]
        # -------------------------------------------------------------
        mode_frame = ttk.Frame(left_panel, padding=5)
        mode_frame.pack(fill="x", pady=(0, 15))
        
        # 가로 균등 분할
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        
        self.btn_latch = tk.Button(
            mode_frame, 
            text="Latch (Dial)", 
            font=("Helvetica", 12, "bold"), 
            bg="#1565C0", 
            fg="white", 
            relief="sunken", 
            bd=3, 
            command=lambda: self.switch_mode("Latch")
        )
        self.btn_latch.grid(row=0, column=0, sticky="ew", padx=2)
        
        self.btn_heatsink = tk.Button(
            mode_frame, 
            text="HeatSink", 
            font=("Helvetica", 12, "bold"), 
            bg="#CFD8DC", 
            fg="#37474F", 
            relief="raised", 
            bd=3, 
            command=lambda: self.switch_mode("HeatSink")
        )
        self.btn_heatsink.grid(row=0, column=1, sticky="ew", padx=2)
        
        # -------------------------------------------------------------
        # [1. Latch 모드용 UI 프레임들 정의]
        # -------------------------------------------------------------
        # 1-1) 레시피 구역
        self.latch_recipe_group = ttk.LabelFrame(left_panel, text=" 레시피 선택 (Recipes) ", padding=10)
        for col in range(2):
            self.latch_recipe_group.columnconfigure(col, weight=1, uniform="latch_rec")
            
        lbl_rubber_l = tk.Label(self.latch_recipe_group, text="Rubber Socket", font=("Helvetica", 9, "bold"))
        lbl_rubber_l.grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        self.combo_rubber_l = ttk.Combobox(self.latch_recipe_group, values=["사용자 입력", "HBM3E", "HBM4", "HBM4E"], state="readonly")
        self.combo_rubber_l.set("사용자 입력")
        self.combo_rubber_l.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.combo_rubber_l.bind("<<ComboboxSelected>>", self.on_latch_recipe_changed)
        
        lbl_offset_l = tk.Label(self.latch_recipe_group, text="Dial Offset", font=("Helvetica", 9, "bold"))
        lbl_offset_l.grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))
        self.combo_offset_l = ttk.Combobox(self.latch_recipe_group, values=["사용자 입력", "HBM3E Latch", "HBM4 Latch"], state="readonly")
        self.combo_offset_l.set("사용자 입력")
        self.combo_offset_l.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 5))
        self.combo_offset_l.bind("<<ComboboxSelected>>", self.on_latch_offset_changed)
        
        # 1-2) 입력 파라미터 구역
        self.latch_input_group = ttk.LabelFrame(left_panel, text=" 입력 파라미터 (Inputs) ", padding=10)
        self.latch_vars = {
            "s_max": tk.DoubleVar(value=0.55),
            "s_hard": tk.DoubleVar(value=0.4),
            "d_h": tk.DoubleVar(value=10.0),
            "dial_val": tk.DoubleVar(value=10.4),
            "dial_offset": tk.DoubleVar(value=0.4)
        }
        self.latch_slider_labels = {}
        self.latch_sliders = {}
        self.create_slider(self.latch_input_group, "Socket 최대 높이 (S_max)", self.latch_vars, self.latch_sliders, self.latch_slider_labels, "s_max", 0.1, 1.5)
        self.create_slider(self.latch_input_group, "Socket Hard Stop (S_hard)", self.latch_vars, self.latch_sliders, self.latch_slider_labels, "s_hard", 0.2, 1.3)
        self.create_slider(self.latch_input_group, "Device 높이 (D_h)", self.latch_vars, self.latch_sliders, self.latch_slider_labels, "d_h", 8.0, 12.0)
        self.create_slider(self.latch_input_group, "Dial 값 (Dial)", self.latch_vars, self.latch_sliders, self.latch_slider_labels, "dial_val", 8.0, 11.0)
        self.create_slider(self.latch_input_group, "Dial Offset (Offset)", self.latch_vars, self.latch_sliders, self.latch_slider_labels, "dial_offset", 0.0, 2.0)
        
        # 1-3) 연산 결과 구역
        self.latch_output_group = ttk.LabelFrame(left_panel, text=" 연산 결과 (Outputs) ", padding=10)
        self.latch_res_space = tk.Label(self.latch_output_group, text="실제 내부 공간 (Space): 0.00 mm", font=("Helvetica", 10, "bold"), fg="#0D47A1")
        self.latch_res_space.pack(anchor="w", pady=2)
        self.latch_res_val1 = tk.Label(self.latch_output_group, text="1) Hard Stop + Device (최소 허용치): 0.00 mm", font=("Helvetica", 10))
        self.latch_res_val1.pack(anchor="w", pady=2)
        self.latch_res_status = tk.Label(self.latch_output_group, text="결과: Pass", font=("Helvetica", 13, "bold"), fg="green")
        self.latch_res_status.pack(anchor="w", pady=10)
        self.latch_res_compression = tk.Label(self.latch_output_group, text="Socket 압축 길이: 0.00 mm", font=("Helvetica", 10))
        self.latch_res_compression.pack(anchor="w", pady=2)
        self.latch_res_gap = tk.Label(self.latch_output_group, text="", font=("Helvetica", 10))
        self.latch_res_gap.pack(anchor="w", pady=2)

        
        # -------------------------------------------------------------
        # [2. HeatSink 모드용 UI 프레임들 정의]
        # -------------------------------------------------------------
        # 2-1) 레시피 구역
        self.heatsink_recipe_group = ttk.LabelFrame(left_panel, text=" 레시피 선택 (Recipes) ", padding=10)
        for col in range(2):
            self.heatsink_recipe_group.columnconfigure(col, weight=1, uniform="hs_rec")
            
        lbl_rubber_h = tk.Label(self.heatsink_recipe_group, text="Rubber Socket", font=("Helvetica", 9, "bold"))
        lbl_rubber_h.grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))
        self.combo_rubber_h = ttk.Combobox(self.heatsink_recipe_group, values=["사용자 입력", "HBM3E", "HBM4", "HBM4E"], state="readonly")
        self.combo_rubber_h.set("사용자 입력")
        self.combo_rubber_h.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.combo_rubber_h.bind("<<ComboboxSelected>>", self.on_heatsink_recipe_changed)
        
        lbl_pcb_h = tk.Label(self.heatsink_recipe_group, text="PCB Type", font=("Helvetica", 9), fg="gray")
        lbl_pcb_h.grid(row=0, column=1, sticky="w", padx=5, pady=(2, 0))
        self.combo_pcb_h = ttk.Combobox(self.heatsink_recipe_group, values=["선택 안 함"], state="disabled")
        self.combo_pcb_h.set("선택 안 함")
        self.combo_pcb_h.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 5))
        
        lbl_guide_h = tk.Label(self.heatsink_recipe_group, text="Guide Type", font=("Helvetica", 9), fg="gray")
        lbl_guide_h.grid(row=2, column=0, sticky="w", padx=5, pady=(2, 0))
        self.combo_guide_h = ttk.Combobox(self.heatsink_recipe_group, values=["선택 안 함"], state="disabled")
        self.combo_guide_h.set("선택 안 함")
        self.combo_guide_h.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        lbl_insert_h = tk.Label(self.heatsink_recipe_group, text="Insert Type", font=("Helvetica", 9), fg="gray")
        lbl_insert_h.grid(row=2, column=1, sticky="w", padx=5, pady=(2, 0))
        self.combo_insert_h = ttk.Combobox(self.heatsink_recipe_group, values=["선택 안 함"], state="disabled")
        self.combo_insert_h.set("선택 안 함")
        self.combo_insert_h.grid(row=3, column=1, sticky="ew", padx=5, pady=(0, 5))
        
        # 2-2) 입력 파라미터 구역
        self.heatsink_input_group = ttk.LabelFrame(left_panel, text=" 입력 파라미터 (Inputs) ", padding=10)
        self.heatsink_vars = {
            "s_max": tk.DoubleVar(value=0.55),
            "s_hard": tk.DoubleVar(value=0.4),
            "d_h": tk.DoubleVar(value=10.0),
            "g_h": tk.DoubleVar(value=4.5),
            "i_h": tk.DoubleVar(value=5.0),
            "h_g": tk.DoubleVar(value=0.9)
        }
        self.heatsink_slider_labels = {}
        self.heatsink_sliders = {}
        self.create_slider(self.heatsink_input_group, "Socket 최대 높이 (S_max)", self.heatsink_vars, self.heatsink_sliders, self.heatsink_slider_labels, "s_max", 0.1, 1.5)
        self.create_slider(self.heatsink_input_group, "Socket Hard Stop (S_hard)", self.heatsink_vars, self.heatsink_sliders, self.heatsink_slider_labels, "s_hard", 0.2, 1.3)
        self.create_slider(self.heatsink_input_group, "Device 높이 (D_h)", self.heatsink_vars, self.heatsink_sliders, self.heatsink_slider_labels, "d_h", 8.0, 12.0)
        self.create_slider(self.heatsink_input_group, "Socket Guide 높이 (G_h)", self.heatsink_vars, self.heatsink_sliders, self.heatsink_slider_labels, "g_h", 3.0, 6.0)
        self.create_slider(self.heatsink_input_group, "Insert 높이 (I_h)", self.heatsink_vars, self.heatsink_sliders, self.heatsink_slider_labels, "i_h", 3.0, 6.0)
        self.create_slider(self.heatsink_input_group, "Heatsink Device 홈 깊이", self.heatsink_vars, self.heatsink_sliders, self.heatsink_slider_labels, "h_g", 0.0, 3.0)
        
        # 2-3) 연산 결과 구역
        self.heatsink_output_group = ttk.LabelFrame(left_panel, text=" 연산 결과 (Outputs) ", padding=10)
        self.heatsink_res_val1 = tk.Label(self.heatsink_output_group, text="1) Hard Stop + Device (최소 허용치): 0.00 mm", font=("Helvetica", 10))
        self.heatsink_res_val1.pack(anchor="w", pady=2)
        self.heatsink_res_val2 = tk.Label(self.heatsink_output_group, text="2) Guide + Insert + Groove (목표치): 0.00 mm", font=("Helvetica", 10))
        self.heatsink_res_val2.pack(anchor="w", pady=2)
        self.heatsink_res_status = tk.Label(self.heatsink_output_group, text="결과: Pass", font=("Helvetica", 13, "bold"), fg="green")
        self.heatsink_res_status.pack(anchor="w", pady=10)
        self.heatsink_res_compression = tk.Label(self.heatsink_output_group, text="Socket 압축 길이: 0.00 mm", font=("Helvetica", 10))
        self.heatsink_res_compression.pack(anchor="w", pady=2)
        self.heatsink_res_gap = tk.Label(self.heatsink_output_group, text="", font=("Helvetica", 10))
        self.heatsink_res_gap.pack(anchor="w", pady=2)

        
        # -------------------------------------------------------------
        # [3. 공통 캔버스 시각화 구역]
        # -------------------------------------------------------------
        self.canvas = tk.Canvas(right_panel, bg="#ECEFF1", highlightthickness=1, highlightbackground="#CFD8DC")
        self.canvas.pack(fill="both", expand=True)
        
        # 리사이즈 핸들러 바인딩
        self.canvas.bind("<Configure>", lambda e: self.update_simulation())
        
        # 초기 모드 적용 및 그리기
        self.switch_mode("Latch")

    def create_slider(self, parent, text, var_dict, slider_dict, label_dict, var_name, from_, to_):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=4)
        lbl = tk.Label(frame, text=text, font=("Helvetica", 9), width=25, anchor="w")
        lbl.pack(side="left")
        val_lbl = tk.Label(frame, text="", font=("Helvetica", 9, "bold"), fg="#1976D2", width=5, anchor="e")
        val_lbl.pack(side="right")
        var = var_dict[var_name]
        
        scale = ttk.Scale(frame, from_=from_, to=to_, variable=var, command=lambda e: self.update_simulation())
        scale.pack(side="right", fill="x", expand=True, padx=5)
        
        slider_dict[var_name] = scale
        label_dict[var_name] = val_lbl

    def switch_mode(self, mode):
        self.current_mode = mode
        
        if mode == "Latch":
            # HeatSink 프레임 숨기기
            self.heatsink_recipe_group.pack_forget()
            self.heatsink_input_group.pack_forget()
            self.heatsink_output_group.pack_forget()
            
            # Latch 프레임 배치
            self.latch_recipe_group.pack(fill="x", pady=5)
            self.latch_input_group.pack(fill="x", pady=5)
            self.latch_output_group.pack(fill="x", pady=10)
            
            # 버튼 시각 효과 갱신
            self.btn_latch.config(bg="#1565C0", fg="white", relief="sunken")
            self.btn_heatsink.config(bg="#CFD8DC", fg="#37474F", relief="raised")
            
            # 캔버스 배경 설정
            self.canvas.config(bg="#ECEFF1", highlightbackground="#CFD8DC")
            
        elif mode == "HeatSink":
            # Latch 프레임 숨기기
            self.latch_recipe_group.pack_forget()
            self.latch_input_group.pack_forget()
            self.latch_output_group.pack_forget()
            
            # HeatSink 프레임 배치
            self.heatsink_recipe_group.pack(fill="x", pady=5)
            self.heatsink_input_group.pack(fill="x", pady=5)
            self.heatsink_output_group.pack(fill="x", pady=10)
            
            # 버튼 시각 효과 갱신
            self.btn_latch.config(bg="#CFD8DC", fg="#37474F", relief="raised")
            self.btn_heatsink.config(bg="#AB47BC", fg="white", relief="sunken")
            
            # 캔버스 배경 설정
            self.canvas.config(bg="#F5F5F7", highlightbackground="#D1D1D6")
            
        self.update_simulation()

    def on_latch_recipe_changed(self, event):
        recipe = self.combo_rubber_l.get()
        if recipe == "HBM3E":
            self.latch_vars["s_max"].set(0.55)
            self.latch_vars["s_hard"].set(0.40)
            self.latch_sliders["s_max"].config(state="disabled")
            self.latch_sliders["s_hard"].config(state="disabled")
        elif recipe == "HBM4":
            self.latch_vars["s_max"].set(0.75)
            self.latch_vars["s_hard"].set(0.50)
            self.latch_sliders["s_max"].config(state="disabled")
            self.latch_sliders["s_hard"].config(state="disabled")
        elif recipe == "HBM4E":
            self.latch_vars["s_max"].set(0.55)
            self.latch_vars["s_hard"].set(0.38)
            self.latch_sliders["s_max"].config(state="disabled")
            self.latch_sliders["s_hard"].config(state="disabled")
        else:  # 사용자 입력
            self.latch_sliders["s_max"].config(state="normal")
            self.latch_sliders["s_hard"].config(state="normal")
            
        self.update_simulation()

    def on_latch_offset_changed(self, event):
        offset_recipe = self.combo_offset_l.get()
        if offset_recipe == "HBM3E Latch":
            self.latch_vars["dial_offset"].set(0.40)
            self.latch_sliders["dial_offset"].config(state="disabled")
        elif offset_recipe == "HBM4 Latch":
            self.latch_vars["dial_offset"].set(0.50)
            self.latch_sliders["dial_offset"].config(state="disabled")
        else:  # 사용자 입력
            self.latch_sliders["dial_offset"].config(state="normal")
            
        self.update_simulation()

    def on_heatsink_recipe_changed(self, event):
        recipe = self.combo_rubber_h.get()
        if recipe == "HBM3E":
            self.heatsink_vars["s_max"].set(0.55)
            self.heatsink_vars["s_hard"].set(0.40)
            self.heatsink_sliders["s_max"].config(state="disabled")
            self.heatsink_sliders["s_hard"].config(state="disabled")
        elif recipe == "HBM4":
            self.heatsink_vars["s_max"].set(0.75)
            self.heatsink_vars["s_hard"].set(0.50)
            self.heatsink_sliders["s_max"].config(state="disabled")
            self.heatsink_sliders["s_hard"].config(state="disabled")
        elif recipe == "HBM4E":
            self.heatsink_vars["s_max"].set(0.55)
            self.heatsink_vars["s_hard"].set(0.38)
            self.heatsink_sliders["s_max"].config(state="disabled")
            self.heatsink_sliders["s_hard"].config(state="disabled")
        else:  # 사용자 입력
            self.heatsink_sliders["s_max"].config(state="normal")
            self.heatsink_sliders["s_hard"].config(state="normal")
            
        self.update_simulation()

    def update_simulation(self):
        # 1. 스냅 처리 및 물리량 가져오기
        if self.current_mode == "Latch":
            recipe = self.combo_rubber_l.get()
            offset_recipe = self.combo_offset_l.get()
            for key, var in self.latch_vars.items():
                if key in ["s_max", "s_hard"] and recipe in ["HBM3E", "HBM4", "HBM4E"]:
                    continue
                if key == "dial_offset" and offset_recipe in ["HBM3E Latch", "HBM4 Latch"]:
                    continue
                val = var.get()
                stepped_val = round(val * 20.0) / 20.0
                if abs(val - stepped_val) > 1e-6:
                    var.set(stepped_val)
                    
            s_max = self.latch_vars["s_max"].get()
            s_hard = self.latch_vars["s_hard"].get()
            d_h = self.latch_vars["d_h"].get()
            dial_val = self.latch_vars["dial_val"].get()
            dial_offset = self.latch_vars["dial_offset"].get()
            
            # 라벨 텍스트 갱신
            for key, lbl in self.latch_slider_labels.items():
                lbl.config(text=f"{self.latch_vars[key].get():.2f}")
                
            space = dial_val + dial_offset
            val1 = s_hard + d_h
            s_initial_stack = s_max + d_h
            
            self.latch_res_space.config(text=f"실제 내부 공간 (Space): {space:.2f} mm")
            self.latch_res_val1.config(text=f"1) Hard Stop + Device (최소 허용치): {val1:.2f} mm")
            
            device_crushed = False
            
            if space < val1 - 1e-5:
                status = "Fail (Over-compressed)"
                color = "#D32F2F"
                comp_len = s_max - s_hard
                short_len = val1 - space
                self.latch_res_status.config(text=f"결과: {status}", fg=color)
                self.latch_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (Hard Stop 도달)")
                self.latch_res_gap.config(text=f"Device 간섭량 (Crushed): {short_len:.2f} mm", fg="#D32F2F")
                heatsink_val = space
                socket_val = s_hard
                device_crushed = True
            elif space >= s_initial_stack - 1e-5:
                status = "Fail (No Contact)"
                color = "#F57C00"
                comp_len = 0.0
                short_len = space - s_initial_stack
                self.latch_res_status.config(text=f"결과: {status}", fg=color)
                self.latch_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (미압축)")
                self.latch_res_gap.config(text=f"모자른 길이 (Gap): {short_len:.2f} mm", fg="#F57C00")
                heatsink_val = space
                socket_val = s_max
            elif abs(val1 - space) < 1e-5:
                status = "Pass"
                color = "#388E3C"
                comp_len = s_initial_stack - space
                self.latch_res_status.config(text=f"결과: {status}", fg=color)
                self.latch_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
                self.latch_res_gap.config(text="")
                heatsink_val = space
                socket_val = space - d_h
            else:
                remaining = space - val1
                status = f"조건부 Pass ({remaining:.2f}mm 부족)"
                color = "#F9A825"
                comp_len = s_initial_stack - space
                self.latch_res_status.config(text=f"결과: {status}", fg=color)
                self.latch_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
                self.latch_res_gap.config(text="")
                heatsink_val = space
                socket_val = space - d_h

        elif self.current_mode == "HeatSink":
            recipe = self.combo_rubber_h.get()
            for key, var in self.heatsink_vars.items():
                if key in ["s_max", "s_hard"] and recipe in ["HBM3E", "HBM4", "HBM4E"]:
                    continue
                val = var.get()
                stepped_val = round(val * 20.0) / 20.0
                if abs(val - stepped_val) > 1e-6:
                    var.set(stepped_val)
                    
            s_max = self.heatsink_vars["s_max"].get()
            s_hard = self.heatsink_vars["s_hard"].get()
            d_h = self.heatsink_vars["d_h"].get()
            g_h = self.heatsink_vars["g_h"].get()
            i_h = self.heatsink_vars["i_h"].get()
            h_g = self.heatsink_vars["h_g"].get()
            
            # 라벨 텍스트 갱신
            for key, lbl in self.heatsink_slider_labels.items():
                lbl.config(text=f"{self.heatsink_vars[key].get():.2f}")
                
            val1 = s_hard + d_h
            val2 = g_h + i_h + h_g
            s_initial_stack = s_max + d_h
            
            self.heatsink_res_val1.config(text=f"1) Hard Stop + Device (최소 허용치): {val1:.2f} mm")
            self.heatsink_res_val2.config(text=f"2) Guide + Insert + Groove (목표치): {val2:.2f} mm")
            
            device_crushed = False
            
            if val2 < val1 - 1e-5:
                status = "Fail (Over-compressed)"
                color = "#D32F2F"
                comp_len = s_max - s_hard
                short_len = val1 - val2
                self.heatsink_res_status.config(text=f"결과: {status}", fg=color)
                self.heatsink_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (Hard Stop 도달)")
                self.heatsink_res_gap.config(text=f"Device 간섭량 (Crushed): {short_len:.2f} mm", fg="#D32F2F")
                heatsink_val = val2
                socket_val = s_hard
                device_crushed = True
            elif val2 >= s_initial_stack - 1e-5:
                status = "Fail (No Contact)"
                color = "#F57C00"
                comp_len = 0.0
                short_len = val2 - s_initial_stack
                self.heatsink_res_status.config(text=f"결과: {status}", fg=color)
                self.heatsink_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm (미압축)")
                self.heatsink_res_gap.config(text=f"모자른 길이 (Gap): {short_len:.2f} mm", fg="#F57C00")
                heatsink_val = val2
                socket_val = s_max
            elif abs(val1 - val2) < 1e-5:
                status = "Pass"
                color = "#388E3C"
                comp_len = s_initial_stack - val2
                self.heatsink_res_status.config(text=f"결과: {status}", fg=color)
                self.heatsink_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
                self.heatsink_res_gap.config(text="")
                heatsink_val = val2
                socket_val = val2 - d_h
            else:
                remaining = val2 - val1
                status = f"조건부 Pass ({remaining:.2f}mm 부족)"
                color = "#F9A825"
                comp_len = s_initial_stack - val2
                self.heatsink_res_status.config(text=f"결과: {status}", fg=color)
                self.heatsink_res_compression.config(text=f"Socket 압축 길이: {comp_len:.2f} mm")
                self.heatsink_res_gap.config(text="")
                heatsink_val = val2
                socket_val = val2 - d_h

        # 2. 캔버스 그리기
        self.canvas.delete("all")
        cx = self.canvas.winfo_width() / 2
        if cx < 100: cx = 400
        base_y = self.canvas.winfo_height() - 80
        if base_y < 100: base_y = 580
        
        SCALE = self.SCALE

        if self.current_mode == "Latch":
            # --- [PCB 바닥판] ---
            self.canvas.create_rectangle(cx-360, base_y, cx+360, base_y+35, fill="#1B5E20", outline="#0D3F12", width=2)
            self.canvas.create_text(cx, base_y+17, text="PCB", fill="white", font=("Helvetica", 11, "bold"))
            
            # --- [Socket] ---
            soc_w = 200
            p_soc_top = base_y - socket_val * SCALE
            self.canvas.create_rectangle(cx - soc_w/2, p_soc_top, cx + soc_w/2, base_y, fill="#FFCA28", outline="#FF8F00", width=2)
            self.canvas.create_text(cx, (p_soc_top + base_y)/2, text="Socket", fill="#5D4037", font=("Helvetica", 10, "bold"))
            
            # --- [Device] ---
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
                
            # --- [ㄷ자 Metal Lid 프레임] ---
            lid_top_y = base_y - 13.5 * SCALE
            lid_leg_bot = base_y
            lid_points = [
                cx - 155, lid_leg_bot,
                cx - 155, lid_top_y,
                cx + 155, lid_top_y,
                cx + 155, lid_leg_bot,
                cx + 130, lid_leg_bot,
                cx + 130, lid_top_y + 30,
                cx - 130, lid_top_y + 30,
                cx - 130, lid_leg_bot
            ]
            self.canvas.create_polygon(lid_points, fill="#CFD8DC", outline="#78909C", width=2)
            
            # --- [Pusher] ---
            hs_w = 215
            p_hs_bottom = base_y - heatsink_val * SCALE
            p_hs_top = p_hs_bottom - 1.8 * SCALE
            self.canvas.create_rectangle(cx - hs_w/2, p_hs_top, cx + hs_w/2, p_hs_bottom, fill="#CFD8DC", outline="#78909C", width=2)
            for step in range(-7, 8):
                line_x = cx + step * 14
                self.canvas.create_line(line_x, p_hs_top + 5, line_x, p_hs_bottom - 5, fill="#B0BEC5", width=1)
            self.canvas.create_text(cx, (p_hs_top + p_hs_bottom)/2, text="Pusher", fill="#37474F", font=("Helvetica", 9, "bold"))
            
            # --- [다이얼 나사축] ---
            shaft_top_y = lid_top_y - 15
            self.canvas.create_rectangle(cx - 12, shaft_top_y, cx + 12, p_hs_top, fill="#B0BEC5", outline="#455A64", width=1.5)
            for sy in range(int(shaft_top_y) + 5, int(p_hs_top) - 5, 6):
                self.canvas.create_line(cx - 12, sy, cx + 12, sy + 3, fill="#455A64", width=1)
                
            # --- [다이얼 노브] ---
            dial_knob_h = 35
            dial_knob_w = 80
            dk_top = lid_top_y - dial_knob_h
            self.canvas.create_rectangle(cx - dial_knob_w/2, dk_top, cx + dial_knob_w/2, lid_top_y, fill="#ECEFF1", outline="#607D8B", width=2)
            for i in range(-5, 6):
                lx = cx + i * 7
                self.canvas.create_line(lx, dk_top + 2, lx, lid_top_y - 2, fill="#B0BEC5", width=2)
            self.canvas.create_rectangle(cx - 25, dk_top - 12, cx + 25, dk_top, fill="#F57C00", outline="#E65100", width=1.5)
            self.canvas.create_text(cx, dk_top - 6, text="DIAL", fill="white", font=("Helvetica", 8, "bold"))
            
            # --- [동적 다이얼 게이지] ---
            gx = cx - 310
            gy = 120
            self.canvas.create_oval(gx - 49, gy - 49, gx + 49, gy + 49, fill="", outline="#90A4AE", width=4)
            self.canvas.create_oval(gx - 45, gy - 45, gx + 45, gy + 45, fill="#F5F5F7", outline="#78909C", width=2)
            for angle_deg in range(0, 360, 30):
                rad = math.radians(angle_deg)
                x1 = gx + 37 * math.cos(rad)
                y1 = gy + 37 * math.sin(rad)
                x2 = gx + 43 * math.cos(rad)
                y2 = gy + 43 * math.sin(rad)
                self.canvas.create_line(x1, y1, x2, y2, fill="#546E7A", width=1)
            gauge_angle = -90 + ((dial_val - 8.0) / (11.0 - 8.0)) * 360
            grad_angle = math.radians(gauge_angle)
            bx = gx + 33 * math.cos(grad_angle)
            by = gy + 33 * math.sin(grad_angle)
            self.canvas.create_line(gx, gy, bx, by, fill="#D32F2F", width=2, arrow=tk.LAST)
            self.canvas.create_oval(gx - 4, gy - 4, gx + 4, gy + 4, fill="#37474F", outline="#212121", width=1)
            self.canvas.create_text(gx, gy - 24, text="DIAL GAUGE", fill="#78909C", font=("Helvetica", 8, "bold"))
            self.canvas.create_text(gx, gy + 24, text=f"{dial_val:.2f} mm", fill="#263238", font=("Helvetica", 10, "bold"))
            
            # --- [참조 지시선 및 화살표] ---
            if device_crushed:
                intended_top = p_dev_bottom - d_h * SCALE
                self.canvas.create_line(cx + 175, intended_top, cx + 175, p_dev_top, fill="red", width=2, arrow=tk.BOTH)
                self.canvas.create_text(cx + 182, (intended_top + p_dev_top)/2, text=f"Crushed {short_len:.2f}mm", fill="red", font=("Helvetica", 9, "bold"), anchor="w")
            elif space >= s_initial_stack - 1e-5:
                self.canvas.create_line(cx, p_dev_top, cx, p_hs_bottom, fill="#F57C00", width=2, arrow=tk.BOTH)
                self.canvas.create_text(cx + 10, (p_dev_top + p_hs_bottom)/2, text=f"Gap {short_len:.2f}mm", fill="#F57C00", font=("Helvetica", 9, "bold"), anchor="w")
                
            limit_y = base_y - val1 * SCALE
            self.canvas.create_line(cx - 350, limit_y, cx + 350, limit_y, fill="#D32F2F", dash=(4, 2))
            self.canvas.create_text(cx - 350, limit_y - 10, text=f"Limit (Hard Stop+Device): {val1:.2f} mm", fill="#D32F2F", font=("Helvetica", 9, "bold"), anchor="w")
            
            space_y = base_y - space * SCALE
            self.canvas.create_line(cx - 350, space_y, cx + 350, space_y, fill="#0D47A1", dash=(4, 2))
            self.canvas.create_text(cx + 350, space_y - 10, text=f"Space (Dial+Offset): {space:.2f} mm", fill="#0D47A1", font=("Helvetica", 9, "bold"), anchor="e")

            # --- [우측 상단 범례 (Legend)] ---
            c_width = self.canvas.winfo_width()
            if c_width < 100: c_width = 800
            legend_x = c_width - 290
            legend_y = 20
            legend_w = 270
            legend_h = 170
            self.canvas.create_rectangle(legend_x, legend_y, legend_x + legend_w, legend_y + legend_h, fill="#FFFFFF", outline="#CFD8DC", width=1.5)
            self.canvas.create_text(legend_x + 15, legend_y + 15, text="💡 다이얼식 소켓 범례", font=("Helvetica", 10, "bold"), fill="#333333", anchor="w")
            items = [
                ("#1B5E20", "PCB (바닥 인쇄회로기판)"),
                ("#FFCA28", "Socket (소켓 커넥터 핀)"),
                ("#2196F3", "Device (테스트 대상 IC 칩)"),
                ("#CFD8DC", "Metal Lid (ㄷ자 프레임 덮개)"),
                ("#CFD8DC", "Pusher (디바이스 가압 블록)")
            ]
            curr_y = legend_y + 40
            for color, desc in items:
                self.canvas.create_rectangle(legend_x + 15, curr_y - 6, legend_x + 27, curr_y + 6, fill=color, outline="#666666")
                self.canvas.create_text(legend_x + 35, curr_y, text=desc, font=("Helvetica", 9), fill="#555555", anchor="w")
                curr_y += 20
            self.canvas.create_line(legend_x + 10, curr_y + 5, legend_x + legend_w - 10, curr_y + 5, fill="#ECEFF1")
            self.canvas.create_text(legend_x + 15, curr_y + 20, text="내부 공간(Space) = Dial + Dial Offset", font=("Helvetica", 8, "bold"), fill="#E65100", anchor="w")

        elif self.current_mode == "HeatSink":
            # --- [PCB] ---
            self.canvas.create_rectangle(cx-380, base_y, cx+380, base_y+40, fill="#2E7D32", outline="#1B5E20", width=2)
            self.canvas.create_text(cx, base_y+20, text="PCB", fill="white", font=("Helvetica", 11, "bold"))
            
            # --- [Yellow: Socket] ---
            soc_w = 180
            p_soc_top = base_y - socket_val * SCALE
            self.canvas.create_rectangle(cx - soc_w/2, p_soc_top, cx + soc_w/2, base_y, fill="#FFCA28", outline="#FF8F00", width=2)
            self.canvas.create_text(cx, (p_soc_top + base_y)/2, text="Socket", fill="#5D4037", font=("Helvetica", 10, "bold"))
            
            # --- [Blue: Device] ---
            dev_w = 210
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
            guide_inner = 105
            guide_outer = 290
            p_guide_top = base_y - g_h * SCALE
            self.canvas.create_rectangle(cx - guide_outer, p_guide_top, cx - guide_inner, base_y, fill="#424242", outline="#212121", width=2)
            self.canvas.create_rectangle(cx + guide_inner, p_guide_top, cx + guide_outer, base_y, fill="#424242", outline="#212121", width=2)
            self.canvas.create_text(cx - (guide_inner + 230)/2, (p_guide_top + base_y)/2, text="Socket Guide", fill="white", font=("Helvetica", 9))
            self.canvas.create_text(cx + (guide_inner + 230)/2, (p_guide_top + base_y)/2, text="Socket Guide", fill="white", font=("Helvetica", 9))
            
            # --- [Mint: Insert] ---
            insert_inner = 110
            insert_outer = 230
            p_insert_bottom = p_guide_top
            p_insert_top = p_insert_bottom - i_h * SCALE
            self.canvas.create_rectangle(cx - insert_outer, p_insert_top, cx - insert_inner, p_insert_bottom, fill="#26A69A", outline="#00796B", width=2)
            self.canvas.create_rectangle(cx + insert_inner, p_insert_top, cx + insert_outer, p_insert_bottom, fill="#26A69A", outline="#00796B", width=2)
            self.canvas.create_text(cx - (insert_inner+insert_outer)/2, (p_insert_top + p_insert_bottom)/2, text="Insert", fill="white", font=("Helvetica", 9))
            self.canvas.create_text(cx + (insert_inner+insert_outer)/2, (p_insert_top + p_insert_bottom)/2, text="Insert", fill="white", font=("Helvetica", 9))
            
            # --- [Silver: Heat Sink (Side View Style)] ---
            hs_outer = 290
            p_hs_groove_top = base_y - heatsink_val * SCALE
            p_hs_rest_bottom = p_hs_groove_top + h_g * SCALE
            
            base_h = 45
            p_hs_base_top_center = p_hs_groove_top - base_h
            p_hs_base_top_side = p_hs_rest_bottom - base_h
            
            base_points = [
                cx - hs_outer, p_hs_base_top_side,
                cx - insert_inner, p_hs_base_top_side,
                cx - insert_inner, p_hs_base_top_center,
                cx + insert_inner, p_hs_base_top_center,
                cx + insert_inner, p_hs_base_top_side,
                cx + hs_outer, p_hs_base_top_side,
                cx + hs_outer, p_guide_top,
                cx + insert_outer, p_guide_top,
                cx + insert_outer, p_hs_rest_bottom,
                cx + insert_inner, p_hs_rest_bottom,
                cx + insert_inner, p_hs_groove_top,
                cx - insert_inner, p_hs_groove_top,
                cx - insert_inner, p_hs_rest_bottom,
                cx - insert_outer, p_hs_rest_bottom,
                cx - insert_outer, p_guide_top,
                cx - hs_outer, p_guide_top
            ]
            self.canvas.create_polygon(base_points, fill="#90A4AE", outline="#455A64", width=2)
            
            # 세로 핀(Fins) 그리기
            fin_top_y = p_hs_groove_top - 95
            for i in range(23):
                fx = cx - 210 + i * 19.09
                if cx - insert_inner + 5 <= fx <= cx + insert_inner - 5:
                    fin_bot_y = p_hs_base_top_center
                else:
                    fin_bot_y = p_hs_base_top_side
                
                self.canvas.create_rectangle(
                    fx - 2.5, fin_top_y, fx + 2.5, fin_bot_y,
                    fill="#CFD8DC", outline="#78909C", width=1
                )
                
            # 가로 핀(Horizontal Fins) 그리기
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
                
            # 스프링 장착 고정 나사 (Spring-loaded Screws) 그리기
            screw_x_positions = [cx - 260, cx + 260]
            for sx in screw_x_positions:
                shaft_top = p_hs_base_top_side - 45
                shaft_bot = p_guide_top + 12
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
                # 스프링 코일
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
                c_width = 800
                
            legend_x = c_width - 290
            legend_y = 20
            legend_w = 270
            legend_h = 210
            
            self.canvas.create_rectangle(
                legend_x, legend_y, legend_x + legend_w, legend_y + legend_h,
                fill="#FFFFFF", outline="#D1D1D6", width=1.5
            )
            self.canvas.create_text(
                legend_x + 15, legend_y + 15,
                text="💡 시뮬레이션 구조 설명",
                font=("Helvetica", 10, "bold"), fill="#333333", anchor="w"
            )
            items = [
                ("#FFCA28", "Yellow: Socket (PCB에 고정)"),
                ("#424242", "Black: Socket Guide (Socket 주변)"),
                ("#42A5F5", "Blue: Device (Socket 위 배치)"),
                ("#26A69A", "Mint: Insert (Guide 위 배치)"),
                ("#90A4AE", "Silver: Heat Sink (모두 덮어 누름)")
            ]
            curr_y = legend_y + 45
            for color, desc in items:
                self.canvas.create_rectangle(
                    legend_x + 15, curr_y - 6, legend_x + 27, curr_y + 6,
                    fill=color, outline="#666666"
                )
                self.canvas.create_text(
                    legend_x + 35, curr_y,
                    text=desc,
                    font=("Helvetica", 9), fill="#555555", anchor="w"
                )
                curr_y += 22
            self.canvas.create_line(
                legend_x + 10, curr_y - 2, legend_x + legend_w - 10, curr_y - 2,
                fill="#E5E5EA"
            )
            curr_y += 13
            self.canvas.create_text(
                legend_x + 15, curr_y,
                text="조건:\n1) <= 2) < (Socket 최대 높이 + Device 높이)",
                font=("Helvetica", 8, "bold"), fill="#E65100", anchor="w", justify="left"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = SocketSimulationTotalApp(root)
    root.mainloop()
