import re
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.scrollview import ScrollView

# --- KV Design ---
KV = """
#:import NoTransition kivy.uix.screenmanager.NoTransition

<InputScreen>:
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        
        MDBoxLayout:
            id: content_container
            orientation: "vertical"
            adaptive_height: True
            padding: dp(10)
            spacing: dp(10)

MDScreen:
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"
        
        # --- 1. Header & Input N (Fixed Height) ---
        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(10)
            padding: dp(10)
            adaptive_height: True
            md_bg_color: [0.96, 0.96, 0.96, 1]

            MDTextField:
                id: size_input
                hint_text: "Ukuran (n)"
                mode: "outlined"
                size_hint_x: 0.3
                input_filter: "int"

            MDButton:
                style: "filled"
                on_release: app.generate_forms()
                size_hint_x: 0.7
                MDButtonText:
                    text: "Buat Input"

        # --- 2. Navigasi Mode (Fixed Height) ---
        MDBoxLayout:
            adaptive_height: True
            spacing: dp(10)
            padding: dp(10), 0, dp(10), dp(5)
            
            MDButton:
                style: "tonal"
                size_hint_x: 0.5
                on_release: app.switch_to("matrix")
                MDButtonText:
                    text: "Mode Matriks"
            
            MDButton:
                style: "tonal"
                size_hint_x: 0.5
                on_release: app.switch_to("equation")
                MDButtonText:
                    text: "Mode Persamaan"

        # --- 3. Area Input (35% Layar) ---
        # Kita batasi tingginya agar tidak memakan tempat hasil
        MDBoxLayout:
            size_hint_y: 0.35
            
            ScreenManager:
                id: screen_manager
                transition: NoTransition()
            
        # --- 4. Area Hasil (65% Layar - LEBIH BESAR) ---
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(10)
            spacing: dp(5)
            size_hint_y: 0.65  # Porsi lebih besar untuk hasil
            md_bg_color: [0.92, 0.94, 1, 1]

            MDButton:
                style: "filled"
                pos_hint: {"center_x": 0.5}
                on_release: app.solve_logic()
                size_hint_y: None
                height: dp(40)
                MDButtonText:
                    text: "Hitung Solusi (Cramer)"

            MDLabel:
                text: "LANGKAH & HASIL:"
                bold: True
                size_hint_y: None
                height: dp(30)
                halign: "center"

            # --- SCROLLVIEW UTAMA HASIL ---
            ScrollView:
                do_scroll_x: True  # Aktifkan scroll horizontal jika matriks melebar
                do_scroll_y: True  # Aktifkan scroll vertikal
                bar_width: dp(12)  # Scrollbar lebih tebal agar mudah disentuh
                bar_color: [0.2, 0.4, 0.8, 0.8] # Warna scrollbar biru

                MDLabel:
                    id: result_label
                    text: "Masukan data di atas lalu klik Hitung..."
                    markup: True
                    valign: "top"
                    
                    # --- KUNCI AGAR BISA SCROLL ---
                    # 1. Matikan size_hint
                    size_hint: None, None
                    # 2. Lebar mengikuti parent (agar wrap) atau lebih lebar jika perlu
                    width: self.parent.width
                    # 3. Tinggi mengikuti isi teks (texture_size)
                    height: self.texture_size[1]
                    # 4. text_size memastikan teks 'wrap' ke bawah
                    text_size: self.width, None
                    
                    padding: dp(10), dp(10)
                    theme_text_color: "Primary"
"""

class InputScreen(Screen):
    pass

class CramerFinalApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        self.n = 0
        self.matrix_inputs = [] 
        self.const_inputs = []  
        self.eq_inputs = []     
        self.current_mode = "matrix" 
        
        return Builder.load_string(KV)

    def on_start(self):
        sm = self.root.ids.screen_manager
        self.screen_matrix = InputScreen(name="matrix")
        self.screen_eq = InputScreen(name="equation")
        sm.add_widget(self.screen_matrix)
        sm.add_widget(self.screen_eq)

    def switch_to(self, mode):
        self.root.ids.screen_manager.current = mode
        self.current_mode = mode

    def generate_forms(self):
        n_text = self.root.ids.size_input.text
        if not n_text: return
        
        try:
            self.n = int(n_text)
            if self.n < 2 or self.n > 6:
                self.root.ids.result_label.text = "Error: n harus 2-6"
                return
        except:
            return

        # 1. Bersihkan
        container_matrix = self.screen_matrix.ids.content_container
        container_eq = self.screen_eq.ids.content_container
        container_matrix.clear_widgets()
        container_eq.clear_widgets()
        
        self.matrix_inputs = []
        self.const_inputs = []
        self.eq_inputs = []

        # 2. BANGUN LAYOUT MATRIKS
        h_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), adaptive_height=True)
        
        grid_a = GridLayout(cols=self.n, spacing=dp(5), size_hint_x=0.75, size_hint_y=None)
        grid_a.bind(minimum_height=grid_a.setter('height')) 
        
        for i in range(self.n):
            row_inputs = []
            for j in range(self.n):
                tf = MDTextField(hint_text=f"a{i+1}{j+1}", mode="outlined", height=dp(48), size_hint_y=None)
                grid_a.add_widget(tf)
                row_inputs.append(tf)
            self.matrix_inputs.append(row_inputs)
        
        grid_b = GridLayout(cols=1, spacing=dp(5), size_hint_x=0.25, size_hint_y=None)
        grid_b.bind(minimum_height=grid_b.setter('height'))

        for i in range(self.n):
            tf = MDTextField(hint_text=f"b{i+1}", mode="filled", height=dp(48), size_hint_y=None)
            grid_b.add_widget(tf)
            self.const_inputs.append(tf)

        h_layout.add_widget(grid_a)
        h_layout.add_widget(grid_b)
        container_matrix.add_widget(MDLabel(text="Matriks A  |  Vektor b", bold=True, adaptive_height=True, halign="center"))
        container_matrix.add_widget(h_layout)

        # 3. BANGUN LAYOUT PERSAMAAN
        container_eq.add_widget(MDLabel(text="Contoh: 2x + y - z = 10", bold=True, adaptive_height=True))
        for i in range(self.n):
            tf = MDTextField(
                hint_text=f"Persamaan {i+1}",
                mode="outlined",
                height=dp(56),
                size_hint_y=None
            )
            container_eq.add_widget(tf)
            self.eq_inputs.append(tf)

        self.root.ids.result_label.text = f"Input n={self.n} siap. Silakan isi data."

    def parse_matrix_mode(self):
        A = []
        b = []
        try:
            for i in range(self.n):
                row = []
                for j in range(self.n):
                    txt = self.matrix_inputs[i][j].text
                    row.append(float(txt) if txt else 0.0)
                A.append(row)
                
                txt_b = self.const_inputs[i].text
                b.append(float(txt_b) if txt_b else 0.0)
            
            vars = [f"x{i+1}" for i in range(self.n)]
            return A, b, vars
        except ValueError:
            return None, None, "Error: Pastikan input matriks berupa angka."

    def parse_equation_mode(self):
        A = []
        b = []
        all_vars = set()
        parsed_data = []

        for tf in self.eq_inputs:
            text = tf.text
            if not text: return None, None, "Ada persamaan kosong."
            
            clean_eq = text.replace(" ", "").lower()
            if "=" not in clean_eq: return None, None, "Format salah (kurang '=')"
            
            lhs, rhs = clean_eq.split("=")
            pattern = r'([+-]?[\d\.]*)([a-z]+)'
            terms = re.findall(pattern, lhs)
            
            coeffs = {}
            for num, var in terms:
                if num in ["", "+"]: val = 1.0
                elif num == "-": val = -1.0
                else: val = float(num)
                coeffs[var] = coeffs.get(var, 0) + val
            
            try: const = float(rhs)
            except: const = 0.0
            
            all_vars.update(coeffs.keys())
            parsed_data.append((coeffs, const))

        sorted_vars = sorted(list(all_vars))
        if len(sorted_vars) != self.n:
            return None, None, f"Jumlah variabel terdeteksi ({len(sorted_vars)}) tidak sama dengan n={self.n}"

        for coeffs, const in parsed_data:
            row = [coeffs.get(var, 0.0) for var in sorted_vars]
            A.append(row)
            b.append(const)
            
        return A, b, sorted_vars

    def format_matrix_text(self, M):
        """Helper: Mengubah list 2D menjadi string format matriks yang rapi."""
        txt = ""
        cols = len(M[0])
        col_widths = [0] * cols
        for row in M:
            for i, val in enumerate(row):
                w = len(f"{val:.1f}")
                if w > col_widths[i]: col_widths[i] = w
        
        for row in M:
            row_str = "| "
            for i, val in enumerate(row):
                row_str += f"{val:>{col_widths[i]}.1f}  "
            row_str += "|\n"
            txt += row_str
        return txt

    def solve_logic(self):
        # Reset text size logic setiap kali hitung
        self.root.ids.result_label.text = "Menghitung..."
        
        if self.current_mode == "matrix":
            A, b, var_names = self.parse_matrix_mode()
        else:
            A, b, var_names = self.parse_equation_mode()

        if A is None:
            self.root.ids.result_label.text = f"[color=red]{var_names}[/color]"
            return

        detA = self.determinant(A)
        
        output = []
        output.append(f"[b][size=20]LANGKAH PENYELESAIAN (CRAMER)[/size][/b]\n")
        
        output.append("[b]1. Matriks Koefisien (A):[/b]")
        output.append(f"[font=RobotoMono-Regular]{self.format_matrix_text(A)}[/font]") 
        output.append(f"Determinan Utama (D) = [b][color=2196F3]{detA:.2f}[/color][/b]\n")

        if abs(detA) < 1e-9:
            output.append("[color=red]D = 0. SPL tidak memiliki solusi tunggal.[/color]")
        else:
            output.append("[b]2. Matriks Pengganti & Variabel:[/b]")
            results = []
            for j in range(self.n):
                Aj = self.replace_column(A, j, b)
                detAj = self.determinant(Aj)
                val = detAj / detA
                var_name = var_names[j]
                
                output.append(f"\n[color=00796B][b]• Variabel {var_name}:[/b][/color]")
                output.append(f"Ganti kolom ke-{j+1} dgn vektor b:")
                output.append(f"[font=RobotoMono-Regular]{self.format_matrix_text(Aj)}[/font]")
                output.append(f"Determinan (D_{var_name}) = {detAj:.2f}")
                output.append(f"{var_name} = {detAj:.2f} / {detA:.2f} = [b][size=16]{val:.4f}[/size][/b]")
                results.append(f"{var_name} = {val:.4f}")

            output.append("\n==============================")
            output.append("[b][size=18]HASIL AKHIR:[/size][/b]")
            output.append(", ".join(results))
            # Tambahkan baris kosong ekstra di bawah agar scroll tidak mentok
            output.append("\n\n") 

        final_text = "\n".join(output)
        self.root.ids.result_label.text = final_text

    def determinant(self, M):
        n = len(M)
        if n == 1: return M[0][0]
        if n == 2: return M[0][0]*M[1][1] - M[0][1]*M[1][0]
        tot = 0
        for c in range(n):
            sub = [[M[r][cc] for cc in range(n) if cc != c] for r in range(1, n)]
            tot += ((-1)**c) * M[0][c] * self.determinant(sub)
        return tot

    def replace_column(self, M, col, vec):
        return [[vec[i] if j == col else M[i][j] for j in range(len(M))] for i in range(len(M))]

if __name__ == "__main__":
    CramerFinalApp().run()