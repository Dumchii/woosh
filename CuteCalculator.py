import tkinter as tk
import math
import os
import sys
#pillow import is required for image handling pls omg, the image is too big, it needs to be resized thanks
from PIL import Image, ImageTk

class HandDrawnCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("CuteCalculator")
        
        #TRANSPARENT BACKGROUND SETUP
        self.root.overrideredirect(True)
        self.transparent_color = "#123456"
        self.root.configure(bg=self.transparent_color)
        self.root.wm_attributes("-transparentcolor", self.transparent_color)
        
        #MAIN CANVAS DIMENSIONS
        self.canvas_width = 460
        self.canvas_height = 520
        self.root.geometry(f"{self.canvas_width}x{self.canvas_height}")
        
        self.expression = ""
        self.current_theme = "light"
        
        #FOOLPROOF IMAGE LOAD
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        sun_path = os.path.join(script_dir, "sun.png")
        moon_path = os.path.join(script_dir, "moon.png")
        
        #PILLOW SIZE TARGET
        target_size = (26, 26)
        
        try:
            #PILLOW RESIZE
            pil_sun = Image.open(sun_path)
            pil_sun_resized = pil_sun.resize(target_size, Image.Resampling.LANCZOS)
            self.sun_img = ImageTk.PhotoImage(pil_sun_resized)
        except Exception as e:
            self.sun_img = None
            print(f"Fallback: sun.png not loaded. Info: {e}")
            
        try:
            pil_moon = Image.open(moon_path)
            pil_moon_resized = pil_moon.resize(target_size, Image.Resampling.LANCZOS)
            self.moon_img = ImageTk.PhotoImage(pil_moon_resized)
        except Exception as e:
            self.moon_img = None
            print(f"Fallback: moon.png not loaded. Info: {e}")
        
        #PALETTE THEMES
        self.themes = {
            "light": {
                "bg_panel": "#B8DB80",      # Matcha green
                "calc_body": "#FFE4EF",     # Pastel pink
                "display": "#F39EB6",       # Deep rose pink
                "display_text": "#F7F6D3",  # Cream white
                "btn_bg": "#B8DB80",        # Matcha button circles
                "btn_text": "#86AF44",      # Dark olive text
                "close_color": "#86AF44"
            },
            "dark": {
                "bg_panel": "#F5B0CB",      
                "calc_body": "#745C97",     
                "display": "#39375B",       
                "display_text": "#F7F6D3",  
                "btn_bg": "#D597CE",        
                "btn_text": "#745C97",      
                "close_color": "#745C97"
            }
        }
        
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg=self.transparent_color, highlightthickness=0)
        self.canvas.pack()
        
        self.click_regions = []
        self.draw_ui()
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1,
            x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2,
            x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,
            x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def draw_ui(self):
        self.canvas.delete("all")
        self.click_regions.clear()
        t = self.themes[self.current_theme]
        
        #BG PANEL
        self.draw_rounded_rect(100, 20, 430, 460, radius=35, fill=t["bg_panel"], outline="")
        
        #CLOSE BUTTON
        self.canvas.create_text(395, 55, text="✕", fill=t["close_color"], font=("Comic Sans MS", 18, "bold"))
        self.click_regions.append({"type": "close", "coords": (395, 55, 15)})
        
        #LIGHT MODE BUTTON
        sun_bg = t["btn_bg"] if self.current_theme == "light" else t["bg_panel"]
        self.canvas.create_rectangle(375, 100, 415, 140, fill=sun_bg, outline="")
        if self.sun_img:
            self.canvas.create_image(395, 120, image=self.sun_img)
        else:
            self.canvas.create_text(395, 120, text="☀️", font=("Comic Sans MS", 16))
        self.click_regions.append({"type": "toggle", "theme": "light", "box": (375, 100, 415, 140)})
        
        #DARK MODE BUTTON
        moon_bg = t["btn_bg"] if self.current_theme == "dark" else t["bg_panel"]
        self.canvas.create_rectangle(375, 145, 415, 185, fill=moon_bg, outline="")
        if self.moon_img:
            self.canvas.create_image(395, 165, image=self.moon_img)
        else:
            self.canvas.create_text(395, 165, text="🌙", font=("Comic Sans MS", 18))
        self.click_regions.append({"type": "toggle", "theme": "dark", "box": (375, 145, 415, 185)})

        #CALCU BOARD
        self.draw_rounded_rect(30, 60, 350, 500, radius=45, fill=t["calc_body"], outline="")
        
        #DISPLAY PANEL
        self.draw_rounded_rect(50, 85, 330, 215, radius=30, fill=t["display"], outline="")
        
        display_val = self.expression if self.expression else "0"
        self.display_text_id = self.canvas.create_text(
            310, 150, text=display_val, anchor="e",
            fill=t["display_text"], font=("Comic Sans MS", 36, "bold")
        )
        
        #BUTTONS
        btn_layout = [
            ['7', '8', '9', '÷'],
            ['6', '5', '4', '×'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]
        
        start_x = 85
        start_y = 260
        spacing_x = 70
        spacing_y = 62
        radius_btn = 24
        
        for row_idx, row in enumerate(btn_layout):
            for col_idx, char in enumerate(row):
                cx = start_x + (col_idx * spacing_x)
                cy = start_y + (row_idx * spacing_y)
                
                self.canvas.create_oval(
                    cx - radius_btn, cy - radius_btn, 
                    cx + radius_btn, cy + radius_btn, 
                    fill=t["btn_bg"], outline=""
                )
                
                label_y_offset = -2 if char in ['-', '+', '÷', '×', '='] else 0
                self.canvas.create_text(
                    cx, cy + label_y_offset, text=char, 
                    fill=t["btn_text"], font=("Comic Sans MS", 15, "bold")
                )
                
                self.click_regions.append({"type": "key", "char": char, "coords": (cx, cy, radius_btn)})

    def on_click(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        for region in self.click_regions:
            if "coords" in region:
                cx, cy, r = region["coords"]
                distance = math.sqrt((event.x - cx)**2 + (event.y - cy)**2)
                if distance <= r:
                    if region["type"] == "key":
                        self.process_input(region["char"])
                    elif region["type"] == "close":
                        self.root.destroy()
                    return
            
            elif "box" in region:
                x1, y1, x2, y2 = region["box"]
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    if region["type"] == "toggle":
                        self.switch_theme(region["theme"])
                    return

    def on_drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        nx = self.root.winfo_x() + dx
        ny = self.root.winfo_y() + dy
        self.root.geometry(f"+{nx}+{ny}")

    def process_input(self, char):
        if char == 'C':
            self.expression = ""
            display_val = "0"
        elif char == '=':
            if self.expression:
                try:
                    result = str(eval(self.expression))
                    if float(result).is_integer():
                        result = str(int(float(result)))
                    self.expression = result  # Save result state
                    display_val = result
                except Exception:
                    display_val = "Error"
                    self.expression = ""
            else:
                display_val = "0"
        elif char in ['+', '-', '×', '÷']:
            if self.expression and self.expression[-1] not in ['+', '-', '*', '/']:
                op_map = {'×': '*', '÷': '/'}
                self.expression += op_map.get(char, char)
            display_val = self.expression if self.expression else "0"
        else:
            self.expression += char
            display_val = self.expression

        #NO OVERFLOW DISPLAY PLS ONG
        text_length = len(display_val)
        if text_length <= 8:
            font_size = 36
        elif text_length <= 12:
            font_size = 26
        elif text_length <= 18:
            font_size = 18
        else:
            font_size = 12  #SMALLEST FONT FOR DIGITS
                    
        self.canvas.itemconfig(
            self.display_text_id, 
            text=display_val, 
            font=("Comic Sans MS", font_size, "bold")
        )

    def switch_theme(self, theme_name):
        if self.current_theme != theme_name:
            self.current_theme = theme_name
            self.draw_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = HandDrawnCalculator(root)
    root.mainloop()