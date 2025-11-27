from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.gridlayout import GridLayout


KV = """
MDScreen:
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(16)

        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(8)
            adaptive_height: True

            MDTextField:
                id: size_input
                hint_text: "Ukuran matriks n (2-6)"
                helper_text: "Contoh: 3 berarti 3 variabel"
                helper_text_mode: "on_focus"
                input_filter: "int"
                max_text_length: 1
                mode: "outlined"

            MDButton:
                style: "filled"
                on_release: app.build_matrices()
                MDButtonText:
                    text: "Buat Matriks"

        MDBoxLayout:
            id: matrix_container
            spacing: dp(16)

        MDButton:
            style: "filled"
            pos_hint: {"center_x": 0.5}
            on_release: app.solve_cramer()
            MDButtonText:
                text: "Hitung Cramer"

        MDLabel:
            text: "HASIL VARIABEL"
            halign: "center"
            bold: True
            size_hint_y: None
            height: dp(30)

        MDLabel:
            id: result_label
            text: "-"
            halign: "center"
            theme_text_color: "Primary"
            size_hint_y: None
            height: dp(130)

        MDLabel:
            text: "LANGKAH PERHITUNGAN CRAMER"
            halign: "center"
            bold: True
            size_hint_y: None
            height: dp(30)

        ScrollView:
            size_hint_y: None
            height: dp(250)
            do_scroll_x: False
            do_scroll_y: True

            MDLabel:
                id: steps_label
                text: "-"
                padding: dp(10), dp(10)
                halign: "left"
                size_hint_y: None
                text_size: self.width, None
                height: self.texture_size[1]
"""


class CramerApp(MDApp):
    def build(self):
        self.coeff_fields = []
        self.const_fields = []
        return Builder.load_string(KV)

    def clear_matrix_container(self):
        c = self.root.ids.matrix_container
        c.clear_widgets()
        self.coeff_fields = []
        self.const_fields = []

    def build_matrices(self):
        size_text = self.root.ids.size_input.text.strip()
        if not size_text:
            self.root.ids.result_label.text = "Masukkan n."
            return

        try:
            n = int(size_text)
        except:
            self.root.ids.result_label.text = "n harus angka."
            return

        if n < 2 or n > 6:
            self.root.ids.result_label.text = "n harus 2 sampai 6."
            return

        self.clear_matrix_container()
        container = self.root.ids.matrix_container

        outer = MDBoxLayout(orientation="horizontal", spacing=dp(16))

        gridA = GridLayout(cols=n, rows=n, spacing=dp(4), size_hint=(0.75, None))
        gridA.bind(minimum_height=gridA.setter("height"))
        self.coeff_fields = []

        for i in range(n):
            row = []
            for j in range(n):
                tf = MDTextField(
                    hint_text=f"a[{i+1},{j+1}]",
                    mode="outlined",
                    size_hint_y=None,
                    height=dp(48)
                )
                gridA.add_widget(tf)
                row.append(tf)
            self.coeff_fields.append(row)

        gridB = GridLayout(cols=1, rows=n, spacing=dp(4), size_hint=(0.25, None))
        gridB.bind(minimum_height=gridB.setter("height"))
        self.const_fields = []

        for i in range(n):
            tf = MDTextField(
                hint_text=f"b[{i+1}]",
                mode="outlined",
                size_hint_y=None,
                height=dp(48)
            )
            gridB.add_widget(tf)
            self.const_fields.append(tf)

        left = MDBoxLayout(orientation="vertical", spacing=dp(6))
        left.add_widget(MDLabel(text="Matriks A", halign="center", size_hint_y=None, height=dp(24)))
        left.add_widget(gridA)

        right = MDBoxLayout(orientation="vertical", spacing=dp(6))
        right.add_widget(MDLabel(text="Vektor b", halign="center", size_hint_y=None, height=dp(24)))
        right.add_widget(gridB)

        outer.add_widget(left)
        outer.add_widget(right)

        container.add_widget(outer)

        self.root.ids.result_label.text = "Isi matriks."
        self.root.ids.steps_label.text = "-"

    def determinant(self, M):
        n = len(M)
        if n == 1: return M[0][0]
        if n == 2: return M[0][0] * M[1][1] - M[0][1] * M[1][0]

        total = 0
        for c in range(n):
            sub = []
            for r in range(1, n):
                row = [M[r][cc] for cc in range(n) if cc != c]
                sub.append(row)
            total += ((-1) ** c) * M[0][c] * self.determinant(sub)
        return total

    def replace_column(self, M, col, newcol):
        return [
            [newcol[i] if j == col else M[i][j] for j in range(len(M))]
            for i in range(len(M))
        ]

    def parse_input(self):
        if not self.coeff_fields:
            return None, None

        n = len(self.coeff_fields)
        A, b = [], []

        try:
            for i in range(n):
                A.append([float(self.coeff_fields[i][j].text or 0) for j in range(n)])
                b.append(float(self.const_fields[i].text or 0))
        except:
            self.root.ids.result_label.text = "Input harus angka."
            return None, None

        return A, b

    def solve_cramer(self):
        A, b = self.parse_input()
        if A is None:
            return

        n = len(A)
        detA = self.determinant(A)

        steps = []
        steps.append(f"det(A) = {detA}")

        if abs(detA) < 1e-12:
            self.root.ids.result_label.text = "det(A)=0. Tidak ada solusi tunggal."
            self.root.ids.steps_label.text = "\n".join(steps)
            return

        solusi = []
        steps.append("")
        steps.append("Langkah tiap variabel:")

        for j in range(n):
            Aj = self.replace_column(A, j, b)
            detAj = self.determinant(Aj)
            xj = detAj / detA

            solusi.append(xj)

            steps.append(f"• det(A{j+1}) = {detAj}")
            steps.append(f"  x{j+1} = det(A{j+1}) / det(A)")
            steps.append(f"  x{j+1} = {detAj} / {detA} = {xj}")
            steps.append("")

        hasil = [f"x{i+1} = {solusi[i]}" for i in range(n)]
        self.root.ids.result_label.text = "\n".join(hasil)
        self.root.ids.steps_label.text = "\n".join(steps)


if __name__ == "__main__":
    CramerApp().run()
