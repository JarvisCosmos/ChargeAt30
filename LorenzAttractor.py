import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, colorchooser

class LorenzAttractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Lorenz Attractor")
        
        # 控制面板
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # 轨迹数量选择
        ttk.Label(self.control_frame, text="轨迹数量:").grid(row=0, column=0)
        self.traj_var = tk.IntVar(value=1)
        self.traj_spin = ttk.Spinbox(self.control_frame, from_=1, to=5, textvariable=self.traj_var)
        self.traj_spin.grid(row=0, column=1)
        
        # 隐藏坐标轴选项
        self.hide_axis_var = tk.BooleanVar()
        self.hide_axis_cb = ttk.Checkbutton(self.control_frame, text="隐藏坐标轴", 
                                          variable=self.hide_axis_var)
        self.hide_axis_cb.grid(row=0, column=2)
        
        # 缩放滑块
        ttk.Label(self.control_frame, text="缩放:").grid(row=0, column=3)
        self.scale_var = tk.DoubleVar(value=1.0)
        self.scale_slider = ttk.Scale(self.control_frame, from_=0.5, to=2.0, 
                                    variable=self.scale_var, command=self.update_scale)
        self.scale_slider.grid(row=0, column=4)
        
        # 速度调节滑块
        ttk.Label(self.control_frame, text="速度:").grid(row=0, column=5)
        self.speed_var = tk.IntVar(value=100)
        self.speed_slider = ttk.Scale(self.control_frame, from_=10, to=500, 
                                    variable=self.speed_var, orient=tk.HORIZONTAL)
        self.speed_slider.grid(row=0, column=6)
        
        # 颜色选择按钮
        ttk.Button(self.control_frame, text="轨迹颜色", 
                 command=self.choose_traj_colors).grid(row=0, column=7)
        ttk.Button(self.control_frame, text="坐标轴颜色", 
                 command=lambda: self.choose_color('axis')).grid(row=0, column=8)
        ttk.Button(self.control_frame, text="背景颜色", 
                 command=lambda: self.choose_color('bg')).grid(row=0, column=9)
        
        # 控制按钮
        self.start_btn = ttk.Button(self.control_frame, text="开始", command=self.start)
        self.start_btn.grid(row=0, column=10)
        self.stop_btn = ttk.Button(self.control_frame, text="停止", state=tk.DISABLED, 
                                command=self.stop)
        self.stop_btn.grid(row=0, column=11)
        
        # 颜色存储
        self.traj_colors = ['blue', 'red', 'green', 'purple', 'orange']
        self.axis_color = 'black'
        self.bg_color = 'white'
        self.running = False
        
        # 绘图区域
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 参数
        self.sigma = 10
        self.rho = 28
        self.beta = 8/3
        self.dt = 0.01
        self.num_steps = 10000
        
    def lorenz(self, x, y, z):
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return dx, dy, dz
    
    def update_scale(self, event=None):
        scale = self.scale_var.get()
        self.ax.set_xlim(-20*scale, 20*scale)
        self.ax.set_ylim(-30*scale, 30*scale)
        self.ax.set_zlim(0, 50*scale)
        self.canvas.draw()
    
    def choose_traj_colors(self):
        num_trajs = self.traj_var.get()
        for i in range(num_trajs):
            color = colorchooser.askcolor(title=f"轨迹{i+1}颜色", 
                                        initialcolor=self.traj_colors[i])[1]
            if color:
                self.traj_colors[i] = color
        self.canvas.draw()

    def choose_color(self, color_type):
        color = colorchooser.askcolor()[1]
        if color:
            if color_type == 'axis':
                self.axis_color = color
                self.ax.xaxis.pane.set_edgecolor(color)
                self.ax.yaxis.pane.set_edgecolor(color)
                self.ax.zaxis.pane.set_edgecolor(color)
            elif color_type == 'bg':
                self.bg_color = color
                self.ax.set_facecolor(color)
                self.fig.set_facecolor(color)
            self.canvas.draw()

    def stop(self):
        self.running = False
        self.start_btn['state'] = tk.NORMAL
        self.stop_btn['state'] = tk.DISABLED

    def start(self):
        self.ax.clear()
        self.ax.set_facecolor(self.bg_color)
        self.fig.set_facecolor(self.bg_color)
        
        if not self.hide_axis_var.get():
            self.ax.xaxis.pane.set_edgecolor(self.axis_color)
            self.ax.yaxis.pane.set_edgecolor(self.axis_color)
            self.ax.zaxis.pane.set_edgecolor(self.axis_color)
            self.ax.set_axis_on()
        else:
            self.ax.set_axis_off()
        
        self.running = True
        self.start_btn['state'] = tk.DISABLED
        self.stop_btn['state'] = tk.NORMAL
        
        num_trajs = self.traj_var.get()
        
        # 初始化所有轨迹的起点和存储
        points = []
        for i in range(num_trajs):
            points.append({
                'x': 0.1 + i*0.01,
                'y': 0,
                'z': 0,
                'xs': [],
                'ys': [],
                'zs': []
            })
        
        # 同时计算和绘制所有轨迹
        for _ in range(self.num_steps):
            if not self.running:
                break
                
            # 计算所有轨迹的下一个点
            for p in points:
                dx, dy, dz = self.lorenz(p['x'], p['y'], p['z'])
                p['x'] += dx * self.dt
                p['y'] += dy * self.dt
                p['z'] += dz * self.dt
                p['xs'].append(p['x'])
                p['ys'].append(p['y'])
                p['zs'].append(p['z'])
            
            # 定期更新图形
            if _ % (1000//self.speed_var.get()) == 0:  # 根据速度调整更新频率
                self.ax.clear()
                if not self.hide_axis_var.get():
                    self.ax.set_axis_on()
                else:
                    self.ax.set_axis_off()
                
                # 绘制所有轨迹
                for i, p in enumerate(points):
                    if p['xs']:
                        self.ax.plot(p['xs'], p['ys'], p['zs'], 
                                   color=self.traj_colors[i], linewidth=0.5)
                
                self.update_scale()
                self.canvas.draw()
                self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = LorenzAttractor(root)
    root.mainloop()
