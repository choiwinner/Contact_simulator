import tkinter as tk
from tkinter import ttk

class SocketSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Rubber Socket Contact Simulator")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        
        self.SCALE = 25
        
        style = ttk.Style()
        style.theme_use('clam')
        
        left_panel = ttk.Frame(root, padding=15, width=420, relief="groove")
        left_panel.pack(side="left", fill="y", expand=False)
        left_panel.pack_propagate(False)
        
        right_panel = ttk.Frame(root, padding=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        title_label = tk.Label(left_panel, text="소켓 접촉 구조 시뮬레이터", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 15))
        
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
        
        self.create_slider(input_group, "Socket 최대 높이 (S_max)", "s_max", 0.1, 1.5)
        self.create_slider(input_group, "Socket Hard Stop (S_hard)", "s_hard", 0.2, 1.3)
        self.create_slider(input_group, "Device 높이 (D_h)", "d_h", 8.0, 12.0)
        self.create_slider(input_group, "Socket Guide 높이 (G_h)", "g_h", 3.0, 6.0)
        self.create_slider(input_group, "Insert 높이 (I_h)", "i_h", 3.0, 6.0)
        self.create_slider(input_group, "Heatsink Device 홈 깊이", "h_g", 0.0, 3.0)
        
        output_group = ttk.LabelFrame(left_panel, text=" 연산 결과 (Outputs) ", padding=10)
        output_group.pack(fill="x", pady=15)
        
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
        
        info_txt = "💡 시뮬레이션 구조 설명:\n" \
                   "- Yellow: Socket (PCB에 고정)\n" \
                   "- Black: Socket Guide (Socket 주변)\n" \
                   "- Blue: Device (Socket 위 배치)\n" \
                   "- Mint: Insert (Guide 위 배치)\n" \
                   "- Purple: Heat Sink (모두 덮어 누름)\n\n" \
                   "조건:\n" \
                   "1) <= 2) < (Socket 최대 높이 + Device 높이)"
        tk.Label(left_panel, text=info_txt, font=("Helvetica", 9), fg="#555", justify="left").pack(side="bottom", fill="x", pady=10)
        
        self.canvas = tk.Canvas(right_panel, bg="#F5F5F7", highlightthickness=1, highlightbackground="#D1D1D6")
        self.canvas.pack(fill="both", expand=True)
        
        # Handle resize
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
        scale = ttk.Scale(frame, from_=from_, to=to_, variable=var, command=lambda e: self.update_simulation())
        scale.pack(side="right", fill="x", expand=True, padx=5)
        self.slider_labels[var_name] = val_lbl

    def update_simulation(self):
        # 0. 입력값 0.05 단위 스냅 (Snap to 0.05)
        for key, var in self.vars.items():
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

        # Update labels (0.05 단위이므로 소수점 둘째 자리까지 표기)
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
        if cx < 100: cx = 280  # Default before layout completes
        base_y = self.canvas.winfo_height() - 50
        if base_y < 100: base_y = 600
        
        SCALE = self.SCALE
        
        # --- [PCB] ---
        self.canvas.create_rectangle(cx-250, base_y, cx+250, base_y+40, fill="#2E7D32", outline="#1B5E20", width=2)
        self.canvas.create_text(cx, base_y+20, text="PCB", fill="white", font=("Helvetica", 11, "bold"))
        
        # --- [Yellow: Socket] ---
        soc_w = 110
        p_soc_top = base_y - socket_val * SCALE
        self.canvas.create_rectangle(cx - soc_w/2, p_soc_top, cx + soc_w/2, base_y, fill="#FFCA28", outline="#FF8F00", width=2)
        self.canvas.create_text(cx, (p_soc_top + base_y)/2, text="Socket", fill="#5D4037", font=("Helvetica", 10, "bold"))
        
        # --- [Blue: Device] ---
        dev_w = 130
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
        guide_inner = 65
        guide_outer = 150
        p_guide_top = base_y - g_h * SCALE
        # Left
        self.canvas.create_rectangle(cx - guide_outer, p_guide_top, cx - guide_inner, base_y, fill="#424242", outline="#212121", width=2)
        # Right
        self.canvas.create_rectangle(cx + guide_inner, p_guide_top, cx + guide_outer, base_y, fill="#424242", outline="#212121", width=2)
        self.canvas.create_text(cx - (guide_inner+guide_outer)/2, (p_guide_top + base_y)/2, text="Socket Guide", fill="white", font=("Helvetica", 9))
        self.canvas.create_text(cx + (guide_inner+guide_outer)/2, (p_guide_top + base_y)/2, text="Socket Guide", fill="white", font=("Helvetica", 9))
        
        # --- [Mint: Insert] ---
        insert_inner = 70
        insert_outer = 150
        p_insert_bottom = p_guide_top
        p_insert_top = p_insert_bottom - i_h * SCALE
        # Left
        self.canvas.create_rectangle(cx - insert_outer, p_insert_top, cx - insert_inner, p_insert_bottom, fill="#26A69A", outline="#00796B", width=2)
        # Right
        self.canvas.create_rectangle(cx + insert_inner, p_insert_top, cx + insert_outer, p_insert_bottom, fill="#26A69A", outline="#00796B", width=2)
        self.canvas.create_text(cx - (insert_inner+insert_outer)/2, (p_insert_top + p_insert_bottom)/2, text="Insert", fill="white", font=("Helvetica", 9))
        self.canvas.create_text(cx + (insert_inner+insert_outer)/2, (p_insert_top + p_insert_bottom)/2, text="Insert", fill="white", font=("Helvetica", 9))
        
        # --- [Purple: Heat Sink] ---
        hs_outer = 170
        p_hs_groove_top = base_y - heatsink_val * SCALE
        p_hs_rest_bottom = p_hs_groove_top + h_g * SCALE
        p_hs_top = p_hs_groove_top - 60
        
        hs_points = [
            cx - hs_outer, p_hs_top,
            cx + hs_outer, p_hs_top,
            cx + hs_outer, p_hs_rest_bottom,
            cx + insert_inner, p_hs_rest_bottom,
            cx + insert_inner, p_hs_groove_top,
            cx - insert_inner, p_hs_groove_top,
            cx - insert_inner, p_hs_rest_bottom,
            cx - hs_outer, p_hs_rest_bottom
        ]
        self.canvas.create_polygon(hs_points, fill="#AB47BC", outline="#6A1B9A", width=2)
        self.canvas.create_text(cx, p_hs_top + 15, text="Heat Sink", fill="white", font=("Helvetica", 11, "bold"))
        
        # --- [Reference Lines & Gap Markers] ---
        # 1) Hard Stop Target
        val1_y = base_y - val1 * SCALE
        self.canvas.create_line(cx - 200, val1_y, cx + 200, val1_y, fill="red", dash=(4, 2))
        self.canvas.create_text(cx - 200, val1_y - 10, text="1) Hard Stop + Device", fill="red", font=("Helvetica", 9, "bold"), anchor="w")
        
        # 2) Structural Close Target
        val2_y = base_y - val2 * SCALE
        self.canvas.create_line(cx - 200, val2_y, cx + 200, val2_y, fill="blue", dash=(4, 2))
        self.canvas.create_text(cx + 200, val2_y - 10, text="2) Structural Close (Val 2)", fill="blue", font=("Helvetica", 9, "bold"), anchor="e")

        # Draw Error Markers
        if device_crushed:
            intended_top = p_dev_bottom - d_h * SCALE
            mid_x = cx + dev_w/2 + 25
            self.canvas.create_line(mid_x, intended_top, mid_x, p_dev_top, fill="red", width=2, arrow=tk.BOTH)
            self.canvas.create_text(mid_x + 5, (intended_top + p_dev_top)/2, text=f"Crushed {short_len:.2f}mm", fill="red", font=("Helvetica", 8, "bold"), anchor="w")
        elif val2 >= s_initial_stack - 1e-5:
            mid_x = cx
            self.canvas.create_line(mid_x, p_dev_top, mid_x, p_hs_groove_top, fill="orange", width=2, arrow=tk.BOTH)
            self.canvas.create_text(mid_x + 5, (p_dev_top + p_hs_groove_top)/2, text=f"Gap {short_len:.2f}mm", fill="orange", font=("Helvetica", 8, "bold"), anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = SocketSimulationApp(root)
    root.mainloop()