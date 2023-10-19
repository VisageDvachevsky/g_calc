import tkinter as tk
import tkinter.ttk as ttk

G = 6.67408e-11

class PlanetSetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("вр")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.planet_setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.planet_setup_tab, text="Настройка планеты")

        self.create_planet_setup_ui()

        self.planet_characteristics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.planet_characteristics_tab, text="Характеристики планеты")

        self.gravitational_potential_label = ttk.Label(self.planet_characteristics_tab, text="Гравитационный потенциал:")
        self.gravitational_potential_label.pack()

        self.gravitational_potential_value = ttk.Label(self.planet_characteristics_tab, text="")
        self.gravitational_potential_value.pack()

        self.create_planet_characteristics_ui()

    def create_planet_setup_ui(self):
        self.labels = ["Масса (кг):", "Радиус:", "Единицы измерения:"]
        self.entries = [ttk.Entry(self.planet_setup_tab) for _ in range(2)]
        self.mass_entry, self.radius_entry = self.entries[0], self.entries[1]
        self.radius_unit_var = tk.StringVar(value="км")
        self.radius_unit_km = ttk.Radiobutton(self.planet_setup_tab, text="км", variable=self.radius_unit_var, value="км")
        self.radius_unit_m = ttk.Radiobutton(self.planet_setup_tab, text="м", variable=self.radius_unit_var, value="м")

        for i, label_text in enumerate(self.labels):
            label = ttk.Label(self.planet_setup_tab, text=label_text)
            label.grid(row=i, column=0)
            if i < 2:
                self.entries[i].grid(row=i, column=1)
            if i == 2:
                self.radius_unit_km.grid(row=i, column=1)
                self.radius_unit_m.grid(row=i, column=2)

        self.atmosphere_var = tk.BooleanVar(value=False)
        self.atmosphere_checkbox = ttk.Checkbutton(self.planet_setup_tab, text="Атмосфера", variable=self.atmosphere_var)
        self.atmosphere_checkbox.grid(row=3, column=0, columnspan=2)

        self.selected_elements = ["Азот (N2)", "Кислород (O2)", "Углекислый газ (CO2)", "Аргон (Ar)", "Неон (Ne)"]
        self.element_labels, self.element_var, self.element_percent_entries = [], [], []

        for i, element in enumerate(self.selected_elements):
            self.element_labels.append(ttk.Label(self.planet_setup_tab, text=element))
            self.element_labels[i].grid(row=i + 4, column=0)
            self.element_var.append(tk.BooleanVar(value=False))
            element_checkbutton = ttk.Checkbutton(self.planet_setup_tab, variable=self.element_var[i])
            element_checkbutton.grid(row=i + 4, column=1)
            element_percent_label = ttk.Label(self.planet_setup_tab, text="Процент:")
            element_percent_label.grid(row=i + 4, column=2)
            element_percent_entry = ttk.Entry(self.planet_setup_tab)
            element_percent_entry.grid(row=i + 4, column=3)
            self.element_percent_entries.append(element_percent_entry)

        self.shape_var = tk.BooleanVar(value=False)
        self.shape_checkbox = ttk.Checkbutton(self.planet_setup_tab, text="Форма", variable=self.shape_var)
        self.shape_checkbox.grid(row=len(self.selected_elements) + 4, column=0, columnspan=2)

        self.shape_choice_label = ttk.Label(self.planet_setup_tab, text="Выбор формы:")
        self.shape_choice_label.grid(row=len(self.selected_elements) + 5, column=0)
        self.shapes = ["Геоид", "Сфера", "Овал", "Другое"]
        self.shape_choice = ttk.Combobox(self.planet_setup_tab, values=self.shapes)
        self.shape_choice.grid(row=len(self.selected_elements) + 5, column=1)

        self.shape_factors = {"Геоид": 1.0, "Сфера": 1.0, "Овал": 1.0, "Другое": 1.0}
        self.atmosphere_effects = {"Азот (N2)": 0.1, "Кислород (O2)": 0.2, "Углекислый газ (CO2)": 0.3, "Аргон (Ar)": 0.05, "Неон (Ne)": 0.02}
        self.g_value = tk.DoubleVar(value=0.0)

        calculate_button = ttk.Button(self.planet_setup_tab, text="Рассчитать", command=self.calculate_gravity)
        calculate_button.grid(row=6 + len(self.selected_elements), column=0, columnspan=2)

        self.result_label = ttk.Label(self.planet_setup_tab, text="")
        self.result_label.grid(row=7 + len(self.selected_elements), column=0, columnspan=2)

    def create_planet_characteristics_ui(self):
        self.earth_characteristics_label = ttk.Label(self.planet_characteristics_tab, text="Характеристики планеты")
        self.earth_characteristics_label.pack()

        self.earth_info_label = ttk.Label(self.planet_characteristics_tab, text="")
        self.earth_info_label.pack()

        self.atmosphere_table = ttk.Treeview(self.planet_characteristics_tab, columns=("Element", "Percentage"), show="headings")
        self.atmosphere_table.heading("Element", text="Вещество")
        self.atmosphere_table.heading("Percentage", text="% в атмосфере")

        self.mass_entry.bind("<KeyRelease>", lambda event: self.update_earth_characteristics())
        self.radius_entry.bind("<KeyRelease>", lambda event: self.update_earth_characteristics())
        self.atmosphere_var.trace_add("write", lambda *args: self.update_earth_characteristics())
        self.shape_var.trace_add("write", lambda *args: self.update_earth_characteristics())
        for i in range(len(self.selected_elements)):
            self.element_var[i].trace_add("write", lambda *args: self.update_earth_characteristics())
            self.element_percent_entries[i].bind("<KeyRelease>", lambda event, idx=i: self.update_earth_characteristics())

    def calculate_gravity(self):
        try:
            mass = float(self.mass_entry.get().replace(',', '.'))
            radius = float(self.radius_entry.get()) * (1000 if self.radius_unit_var.get() == "км" else 1)
            atmosphere_data = [(self.element_labels[i]["text"], float(self.element_percent_entries[i].get())) for i in range(len(self.selected_elements)) if self.element_var[i].get()]
            custom_shape = self.shape_factors.get(self.shape_choice.get(), 1.0)

            g = -((G * mass) / (radius ** 2))

            if self.shape_var.get():
                g = g * custom_shape

            for element_name, element_percentage in atmosphere_data:
                effect = self.atmosphere_effects.get(element_name, 0)
                g -= (element_percentage / 100 * g * effect)

            self.g_value.set(g)
            self.update_earth_characteristics()
        except ValueError:
            self.result_label.config(text="Введите корректные данные.")

    def update_earth_characteristics(self):
        mass_str = self.mass_entry.get()
        radius_str = self.radius_entry.get()

        if mass_str and radius_str:
            mass_value = float(mass_str.replace(',', '.'))
            selected_radius = float(radius_str)

            earth_info = f"Масса: {self.mass_entry.get()} кг\n"
            earth_info += f"Радиус: {self.radius_entry.get()} {self.radius_unit_var.get()}\n"
            earth_info += f"Атмосфера: {'Есть' if self.atmosphere_var.get() else 'Отсутствует'}\n"
            earth_info += f"Форма планеты: {self.shape_choice.get() if self.shape_var.get() else 'Не выбрана'}\n"
            earth_info += f"Ускорение свободного падения (g): {self.g_value.get():.2f} м/с^2\n"

            self.earth_info_label.config(text=earth_info)

            self.atmosphere_table.delete(*self.atmosphere_table.get_children())
            if self.atmosphere_var.get():
                for i in range(len(self.selected_elements)):
                    element_name = self.element_labels[i]["text"]
                    is_selected = self.element_var[i].get()
                    if is_selected:
                        element_percentage = self.element_percent_entries[i].get()
                        self.atmosphere_table.insert("", "end", values=(element_name, element_percentage))

            selected_radius = self.radius_entry.get()
            if not selected_radius:
                selected_radius = 0
            else:
                selected_radius = float(selected_radius)
                if self.radius_unit_var.get() == "км":
                    selected_radius *= 1000

            if selected_radius != 0:
                gravitational_potential = G * mass_value / selected_radius
                self.gravitational_potential_value.config(text=f"{gravitational_potential:.2e} Дж/кг")
            else:
                self.gravitational_potential_value.config(text="Радиус не может быть равен нулю.")
        else:
            self.earth_info_label.config(text="Масса и радиус должны быть числами.")

    def update_atmosphere_fields(self):
        if self.atmosphere_var.get():
            for i in range(len(self.selected_elements)):
                self.element_labels[i].grid()
                self.element_var[i].set(0)
                self.element_percent_entries[i].grid()
        else:
            for i in range(len(self.selected_elements)):
                self.element_labels[i].grid_remove()
                self.element_var[i].set(0)
                self.element_percent_entries[i].grid_remove()

    def update_atmosphere_table(self):
        if self.atmosphere_var.get():
            self.atmosphere_table.pack()
        else:
            self.atmosphere_table.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = PlanetSetupApp(root)
    root.mainloop()
