import tkinter as tk
from tkinter import messagebox
import math


# ======================================
# CLASE GRAFO (LOGICA)
# ======================================
class Graph:

    def __init__(self):
        self.nodes = {}  # {nombre: (x, y)}
        self.edges = {}  # {(nodo1, nodo2): peso}

    def add_node(self, node, x, y):
        if node in self.nodes:
            return "exists"
        self.nodes[node] = (x, y)
        return "success"

    def add_edge(self, node1, node2, weight):
        if node1 not in self.nodes or node2 not in self.nodes:
            return "missing"
        self.edges[(node1, node2)] = weight
        return "success"

    def reset(self):
        self.nodes.clear()
        self.edges.clear()

    def delete_node(self, node):
        if node not in self.nodes:
            return "missing"
        del self.nodes[node]
        self.edges = {
            (node1, node2): weight
            for (node1, node2), weight in self.edges.items()
            if node1 != node and node2 != node
        }
        return "success"


# ======================================
# CLASE VISUALIZADOR (CANVAS)
# ======================================
class GraphVisualizer:

    def __init__(self, canvas, graph):
        self.canvas = canvas
        self.graph = graph
        self.node_radius = 20

    def draw(
        self,
        active_nodes=None,
        visited_nodes=None,
        active_edges=None,
        selected_edges=None,
        pointers=None,
        result_nodes=None,
    ):
        self.canvas.delete("all")

        active_nodes = active_nodes or set()
        visited_nodes = visited_nodes or set()
        active_edges = active_edges or set()
        selected_edges = selected_edges or set()
        pointers = pointers or {}
        result_nodes = result_nodes or set()

        # Dibujar Aristas (Flechas)
        for (node1, node2), weight in self.graph.edges.items():
            x1, y1 = self.graph.nodes[node1]
            x2, y2 = self.graph.nodes[node2]

            # Calcular el ajuste para que la flecha no quede oculta bajo el circulo del nodo
            angle = math.atan2(y2 - y1, x2 - x1)
            r = self.node_radius

            # Ajustamos el punto final para que la punta de la flecha toque el borde del nodo
            x2_adj = x2 - r * math.cos(angle)
            y2_adj = y2 - r * math.sin(angle)
            x1_adj = x1 + r * math.cos(angle)
            y1_adj = y1 + r * math.sin(angle)

            edge_key = (node1, node2)
            edge_color = "#34495e"
            edge_width = 2

            if edge_key in selected_edges:
                edge_color = "#2ecc71"
                edge_width = 3
            elif edge_key in active_edges:
                edge_color = "#e74c3c"
                edge_width = 3

            # arrow=tk.LAST dibuja la flecha apuntando al nodo destino
            self.canvas.create_line(
                x1_adj,
                y1_adj,
                x2_adj,
                y2_adj,
                arrow=tk.LAST,
                arrowshape=(12, 15, 5),
                width=edge_width,
                fill=edge_color,
            )

            # Etiqueta de peso
            mx = (x1_adj + x2_adj) / 2
            my = (y1_adj + y2_adj) / 2
            self.canvas.create_text(
                mx,
                my - 8,
                text=str(weight),
                fill="#2c3e50",
                font=("Arial", 9, "bold"),
            )

        # Dibujar Nodos
        for node, (x, y) in self.graph.nodes.items():
            r = self.node_radius
            fill_color = "#3498db"
            outline_color = "#2980b9"

            if node in visited_nodes:
                fill_color = "#2ecc71"
                outline_color = "#27ae60"
            if node in active_nodes:
                fill_color = "#f1c40f"
                outline_color = "#f39c12"
            if node in result_nodes:
                fill_color = "#9b59b6"
                outline_color = "#8e44ad"

            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=fill_color,
                outline=outline_color,
                width=2,
            )
            self.canvas.create_text(
                x, y, text=node, fill="white", font=("Arial", 10, "bold")
            )

        # Dibujar punteros
        for node, label in pointers.items():
            if node not in self.graph.nodes:
                continue
            x, y = self.graph.nodes[node]
            self.canvas.create_text(
                x,
                y - self.node_radius - 10,
                text=label,
                fill="#c0392b",
                font=("Arial", 9, "bold"),
            )


# ======================================
# INTERFAZ GRÁFICA PRINCIPAL (APP)
# ======================================
class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Grafos Dirigidos")
        self.root.geometry("900x600")

        self.graph = Graph()

        # Contenedor Izquierdo (Controles con desplazamiento)
        self.control_container = tk.Frame(root, width=250, bg="#f0f0f0")
        self.control_container.pack(side=tk.LEFT, fill=tk.Y)

        self.control_canvas = tk.Canvas(
            self.control_container, bg="#f0f0f0", highlightthickness=0
        )
        self.control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.control_scrollbar = tk.Scrollbar(
            self.control_container,
            orient=tk.VERTICAL,
            command=self.control_canvas.yview,
        )
        self.control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)

        self.control_frame = tk.Frame(
            self.control_canvas, width=250, bg="#f0f0f0", padx=10, pady=10
        )
        self.control_window = self.control_canvas.create_window(
            (0, 0), window=self.control_frame, anchor="nw"
        )

        self.control_frame.bind("<Configure>", self.on_control_configure)
        self.control_canvas.bind("<Configure>", self.on_control_canvas_configure)
        self.control_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Panel derecho (Eliminar nodo)
        self.right_frame = tk.Frame(root, width=160, bg="#f7f7f7", padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas (Área de dibujo)
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.visualizer = GraphVisualizer(self.canvas, self.graph)

        self.steps = []
        self.step_index = 0
        self.auto_running = False
        self.animation_after_id = None
        self.step_delay_ms = 800

        self.create_widgets()

    def create_widgets(self):
        # --- SECCIÓN AGREGAR NODO ---
        tk.Label(
            self.control_frame,
            text="AGREGAR NODO",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
        ).pack(pady=5)

        tk.Label(self.control_frame, text="Nombre del Nodo:", bg="#f0f0f0").pack(
            anchor="w"
        )
        self.node_entry = tk.Entry(self.control_frame)
        self.node_entry.pack(fill=tk.X, pady=2)

        # Radio buttons para cambiar entre modo Manual y Automático
        self.placement_mode = tk.StringVar(value="auto")

        tk.Radiobutton(
            self.control_frame,
            text="Posición Automática",
            variable=self.placement_mode,
            value="auto",
            command=self.toggle_position_entries,
            bg="#f0f0f0",
        ).pack(anchor="w", pady=2)

        tk.Radiobutton(
            self.control_frame,
            text="Posición Manual",
            variable=self.placement_mode,
            value="manual",
            command=self.toggle_position_entries,
            bg="#f0f0f0",
        ).pack(anchor="w", pady=2)

        # Entradas de posición (se deshabilitan si es automático)
        self.pos_frame = tk.Frame(self.control_frame, bg="#f0f0f0")
        self.pos_frame.pack(fill=tk.X, pady=5)

        tk.Label(self.pos_frame, text="X:", bg="#f0f0f0").grid(row=0, column=0)
        self.x_entry = tk.Entry(self.pos_frame, width=7, state=tk.DISABLED)
        self.x_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.pos_frame, text="Y:", bg="#f0f0f0").grid(row=0, column=2)
        self.y_entry = tk.Entry(self.pos_frame, width=7, state=tk.DISABLED)
        self.y_entry.grid(row=0, column=3, padx=5)

        tk.Button(
            self.control_frame,
            text="Agregar Nodo",
            command=self.add_node,
            bg="#2ecc71",
            fg="white",
        ).pack(fill=tk.X, pady=5)

        tk.Button(
            self.control_frame,
            text="Eliminar Nodo",
            command=self.delete_node,
            bg="#c0392b",
            fg="white",
        ).pack(fill=tk.X, pady=5)

        tk.Frame(self.control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(
            fill=tk.X, pady=10
        )

        # --- SECCIÓN AGREGAR ARISTA ---
        tk.Label(
            self.control_frame,
            text="AGREGAR CONEXIÓN (ARISTA)",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
        ).pack(pady=5)

        tk.Label(self.control_frame, text="Desde Nodo:", bg="#f0f0f0").pack(anchor="w")
        self.edge1_entry = tk.Entry(self.control_frame)
        self.edge1_entry.pack(fill=tk.X, pady=2)

        tk.Label(self.control_frame, text="Hacia Nodo:", bg="#f0f0f0").pack(anchor="w")
        self.edge2_entry = tk.Entry(self.control_frame)
        self.edge2_entry.pack(fill=tk.X, pady=2)

        tk.Label(self.control_frame, text="Peso:", bg="#f0f0f0").pack(anchor="w")
        self.weight_entry = tk.Entry(self.control_frame)
        self.weight_entry.insert(0, "1")
        self.weight_entry.pack(fill=tk.X, pady=2)

        tk.Button(
            self.control_frame,
            text="Conectar Nodos",
            command=self.add_edge,
            bg="#e67e22",
            fg="white",
        ).pack(fill=tk.X, pady=5)

        tk.Frame(self.control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(
            fill=tk.X, pady=10
        )

        # --- SECCION ALGORITMOS ---
        tk.Label(
            self.control_frame,
            text="ALGORITMOS",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
        ).pack(pady=5)

        tk.Label(self.control_frame, text="Nodo inicio:", bg="#f0f0f0").pack(anchor="w")
        self.start_entry = tk.Entry(self.control_frame)
        self.start_entry.pack(fill=tk.X, pady=2)

        tk.Label(self.control_frame, text="Nodo destino:", bg="#f0f0f0").pack(
            anchor="w"
        )
        self.end_entry = tk.Entry(self.control_frame)
        self.end_entry.pack(fill=tk.X, pady=2)

        tk.Button(
            self.control_frame,
            text="Dijkstra",
            command=self.run_dijkstra,
            bg="#8e44ad",
            fg="white",
        ).pack(fill=tk.X, pady=3)
        tk.Button(
            self.control_frame,
            text="Floyd",
            command=self.run_floyd,
            bg="#9b59b6",
            fg="white",
        ).pack(fill=tk.X, pady=3)
        tk.Button(
            self.control_frame,
            text="Floyd guarda vertices",
            command=self.run_floyd_vertices,
            bg="#9b59b6",
            fg="white",
        ).pack(fill=tk.X, pady=3)
        tk.Button(
            self.control_frame,
            text="Warshall",
            command=self.run_warshall,
            bg="#9b59b6",
            fg="white",
        ).pack(fill=tk.X, pady=3)
        tk.Button(
            self.control_frame,
            text="Prim (N)",
            command=self.run_prim,
            bg="#16a085",
            fg="white",
        ).pack(fill=tk.X, pady=3)
        tk.Button(
            self.control_frame,
            text="Kruskal (N)",
            command=self.run_kruskal,
            bg="#16a085",
            fg="white",
        ).pack(fill=tk.X, pady=3)

        tk.Frame(self.control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(
            fill=tk.X, pady=10
        )

        # --- CONTROL DE PASOS ---
        tk.Label(
            self.control_frame,
            text="CONTROL DE PASOS",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
        ).pack(pady=5)

        self.status_label = tk.Label(
            self.control_frame,
            text="Paso: -",
            bg="#f0f0f0",
            justify=tk.LEFT,
            wraplength=220,
        )
        self.status_label.pack(fill=tk.X, pady=4)

        tk.Button(
            self.control_frame,
            text="Paso siguiente",
            command=self.next_step,
            bg="#34495e",
            fg="white",
        ).pack(fill=tk.X, pady=3)
        tk.Button(
            self.control_frame,
            text="Auto",
            command=self.start_auto,
            bg="#34495e",
            fg="white",
        ).pack(fill=tk.X, pady=3)
        tk.Button(
            self.control_frame,
            text="Detener",
            command=self.stop_animation,
            bg="#34495e",
            fg="white",
        ).pack(fill=tk.X, pady=3)

        tk.Frame(self.control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(
            fill=tk.X, pady=10
        )

        # --- RESULTADOS ---
        tk.Label(
            self.control_frame,
            text="RESULTADOS",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
        ).pack(pady=5)

        self.output_text = tk.Text(self.control_frame, height=9, width=28, wrap=tk.WORD)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.pack(fill=tk.X, pady=5)

        tk.Frame(self.control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(
            fill=tk.X, pady=10
        )

        # --- BOTONES DE SISTEMA ---
        tk.Button(
            self.control_frame,
            text="Resetear Grafo",
            command=self.reset_graph,
            bg="#e74c3c",
            fg="white",
        ).pack(fill=tk.X, pady=5)
        tk.Button(
            self.control_frame,
            text="Salir",
            command=self.exit_program,
            bg="#95a5a6",
            fg="white",
        ).pack(fill=tk.X, pady=5)

        # --- PANEL DERECHO ---
        tk.Label(
            self.right_frame,
            text="ELIMINAR",
            font=("Arial", 10, "bold"),
            bg="#f7f7f7",
        ).pack(pady=5)

        tk.Label(self.right_frame, text="Nodo:", bg="#f7f7f7").pack(anchor="w")
        self.delete_entry = tk.Entry(self.right_frame)
        self.delete_entry.pack(fill=tk.X, pady=2)

        tk.Button(
            self.right_frame,
            text="Eliminar",
            command=self.delete_node,
            bg="#c0392b",
            fg="white",
        ).pack(fill=tk.X, pady=5)

    def toggle_position_entries(self):
        """Activa o desactiva los campos X e Y según el modo seleccionado."""
        if self.placement_mode.get() == "manual":
            self.x_entry.config(state=tk.NORMAL)
            self.y_entry.config(state=tk.NORMAL)
        else:
            self.x_entry.config(state=tk.DISABLED)
            self.y_entry.config(state=tk.DISABLED)

    def on_control_configure(self, event):
        self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))

    def on_control_canvas_configure(self, event):
        self.control_canvas.itemconfig(self.control_window, width=event.width)

    def on_mousewheel(self, event):
        if self.control_canvas.winfo_containing(event.x_root, event.y_root) is None:
            return
        self.control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def arrange_nodes_automatically(self):
        """Redistribuye todos los nodos automáticos en una formación circular."""
        # Filtramos o simplemente recalculamos todos para que queden armónicos
        num_nodes = len(self.graph.nodes)
        if num_nodes == 0:
            return

        # Centro del canvas aproximado
        center_x = 300
        center_y = 300
        radius = 150

        for i, node in enumerate(self.graph.nodes.keys()):
            # Si quieres respetar estrictamente los manuales anteriores, podrías saltártelos,
            # pero recalcular armónicamente previene colisiones.
            angle = i * (2 * math.pi / num_nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.graph.nodes[node] = (int(x), int(y))

    # =========================
    # AGREGAR NODO
    # =========================
    def add_node(self):
        node = self.node_entry.get().strip()

        # Validación 1: Entrada vacía
        if not node:
            messagebox.showerror(
                "Error de Entrada", "El nombre del nodo no puede estar vacío."
            )
            return

        # Validación 2: Que sea estrictamente un número
        if not node.isdigit():
            messagebox.showerror(
                "Error de Tipo", "El valor del nodo debe ser un número entero."
            )
            return

        mode = self.placement_mode.get()

        if mode == "manual":
            # Validaciones para el modo manual
            x_str = self.x_entry.get().strip()
            y_str = self.y_entry.get().strip()

            if not x_str or not y_str:
                messagebox.showerror(
                    "Error", "Debe ingresar las posiciones X e Y en modo manual."
                )
                return

            try:
                x = int(x_str)
                y = int(y_str)
            except ValueError:
                messagebox.showerror(
                    "Error", "Las posiciones X e Y deben ser números enteros."
                )
                return
        else:
            # Modo Automático: Asignamos posición temporal (se acomodará al redibujar)
            x, y = 0, 0

        result = self.graph.add_node(node, x, y)

        if result == "exists":
            messagebox.showerror("Error", f"El nodo '{node}' ya existe.")
            return

        # Si el modo es automático, recalculamos las posiciones circulares de los nodos
        if mode == "auto":
            self.arrange_nodes_automatically()

        self.visualizer.draw()

        # Limpieza de campos
        self.node_entry.delete(0, tk.END)
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)

    # =========================
    # AGREGAR ARISTA
    # =========================
    def add_edge(self):
        node1 = self.edge1_entry.get().strip()
        node2 = self.edge2_entry.get().strip()
        weight_str = self.weight_entry.get().strip()

        # Validaciones de aristas
        if not node1 or not node2:
            messagebox.showerror(
                "Error", "Debe ingresar ambos nodos para establecer una conexión."
            )
            return

        if not node1.isdigit() or not node2.isdigit():
            messagebox.showerror(
                "Error", "Los nombres de los nodos deben ser numéricos."
            )
            return

        weight = self.parse_weight(weight_str)
        if weight is None:
            messagebox.showerror("Error", "El peso debe ser un numero valido.")
            return

        result = self.graph.add_edge(node1, node2, weight)

        if result == "missing":
            messagebox.showerror("Error", "Uno o ambos nodos no existen.")
        else:
            self.visualizer.draw()

        self.edge1_entry.delete(0, tk.END)
        self.edge2_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.weight_entry.insert(0, "1")

    # =========================
    # ELIMINAR NODO
    # =========================
    def delete_node(self):
        node = self.delete_entry.get().strip()
        if not node:
            messagebox.showerror("Error", "Debe indicar el nodo a eliminar.")
            return
        if not node.isdigit():
            messagebox.showerror(
                "Error", "El nombre del nodo debe ser un número entero."
            )
            return

        result = self.graph.delete_node(node)
        if result == "missing":
            messagebox.showerror("Error", "El nodo no existe.")
            return

        if self.placement_mode.get() == "auto":
            self.arrange_nodes_automatically()

        self.visualizer.draw()
        self.clear_steps()
        self.delete_entry.delete(0, tk.END)

    # =========================
    # RESETEAR
    # =========================
    def reset_graph(self):
        if messagebox.askyesno("Resetear", "¿Deseas borrar el grafo completo?"):
            self.graph.reset()
            self.visualizer.draw()
            self.clear_steps()

    # =========================
    # SALIR
    # =========================
    def exit_program(self):
        if messagebox.askyesno("Salir", "¿Deseas cerrar el programa?"):
            self.root.destroy()

    # =========================
    # UTILIDADES
    # =========================
    def parse_weight(self, weight_str):
        if not weight_str:
            return 1
        try:
            value = float(weight_str)
        except ValueError:
            return None
        if value.is_integer():
            return int(value)
        return value

    def format_number(self, value):
        if value == math.inf:
            return "INF"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        if isinstance(value, float):
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return str(value)

    def format_matrix(self, matrix, nodes):
        header = "    " + " ".join(f"{n:>6}" for n in nodes)
        lines = [header]
        for i, row in enumerate(matrix):
            row_values = []
            for val in row:
                if isinstance(val, bool):
                    cell = "1" if val else "0"
                elif val is None:
                    cell = "-"
                else:
                    cell = self.format_number(val)
                row_values.append(f"{cell:>6}")
            lines.append(f"{nodes[i]:>3} " + " ".join(row_values))
        return "\n".join(lines)

    def get_sorted_nodes(self):
        try:
            return sorted(self.graph.nodes.keys(), key=lambda n: int(n))
        except ValueError:
            return sorted(self.graph.nodes.keys())

    def build_adjacency(self, undirected=False):
        adjacency = {n: [] for n in self.graph.nodes}
        for (node1, node2), weight in self.graph.edges.items():
            adjacency[node1].append((node2, weight))
            if undirected:
                adjacency[node2].append((node1, weight))
        return adjacency

    def get_undirected_edges(self):
        edges = {}
        for (node1, node2), weight in self.graph.edges.items():
            if node1 == node2:
                continue
            try:
                key = tuple(sorted([node1, node2], key=lambda n: int(n)))
            except ValueError:
                key = tuple(sorted([node1, node2]))
            if key not in edges or weight < edges[key]:
                edges[key] = weight
        return [(node1, node2, weight) for (node1, node2), weight in edges.items()]

    def edge_for_draw(self, node1, node2):
        if (node1, node2) in self.graph.edges:
            return (node1, node2)
        if (node2, node1) in self.graph.edges:
            return (node2, node1)
        return (node1, node2)

    def merge_pointers(self, pointer_maps):
        merged = {}
        for pointer_map in pointer_maps:
            for node, label in pointer_map.items():
                if node in merged:
                    merged[node] = f"{merged[node]}/{label}"
                else:
                    merged[node] = label
        return merged

    # =========================
    # CONTROL DE PASOS
    # =========================
    def clear_steps(self):
        self.stop_animation()
        self.steps = []
        self.step_index = 0
        self.status_label.config(text="Paso: -")
        self.set_output("")

    def set_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)

    def load_steps(self, steps):
        self.stop_animation()
        self.steps = steps
        self.step_index = 0
        if not self.steps:
            self.status_label.config(text="Paso: -")
            return
        self.show_step(0)

    def show_step(self, index):
        if not self.steps:
            return
        step = self.steps[index]
        self.visualizer.draw(
            active_nodes=step.get("active_nodes"),
            visited_nodes=step.get("visited_nodes"),
            active_edges=step.get("active_edges"),
            selected_edges=step.get("selected_edges"),
            pointers=step.get("pointers"),
            result_nodes=step.get("result_nodes"),
        )
        desc = step.get("desc", "")
        self.status_label.config(text=f"Paso {index + 1}/{len(self.steps)}: {desc}")
        if "output" in step:
            self.set_output(step["output"])

    def next_step(self):
        if not self.steps:
            return
        self.stop_animation()
        if self.step_index < len(self.steps) - 1:
            self.step_index += 1
            self.show_step(self.step_index)

    def start_auto(self):
        if not self.steps:
            return
        if self.auto_running:
            return
        self.auto_running = True
        self.schedule_auto()

    def schedule_auto(self):
        if not self.auto_running:
            return
        if self.step_index >= len(self.steps) - 1:
            self.auto_running = False
            return
        self.step_index += 1
        self.show_step(self.step_index)
        self.animation_after_id = self.root.after(
            self.step_delay_ms, self.schedule_auto
        )

    def stop_animation(self):
        self.auto_running = False
        if self.animation_after_id is not None:
            self.root.after_cancel(self.animation_after_id)
            self.animation_after_id = None

    # =========================
    # ALGORITMOS
    # =========================
    def run_dijkstra(self):
        if not self.graph.nodes:
            messagebox.showerror("Error", "No hay nodos en el grafo.")
            return
        if not self.graph.edges:
            messagebox.showerror("Error", "No hay aristas en el grafo.")
            return

        for weight in self.graph.edges.values():
            if weight < 0:
                messagebox.showerror("Error", "Dijkstra requiere pesos no negativos.")
                return

        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()

        if not start:
            messagebox.showerror("Error", "Debe indicar el nodo inicio.")
            return
        if start not in self.graph.nodes:
            messagebox.showerror("Error", "El nodo inicio no existe.")
            return
        if end and end not in self.graph.nodes:
            messagebox.showerror("Error", "El nodo destino no existe.")
            return

        nodes = self.get_sorted_nodes()
        adjacency = self.build_adjacency(undirected=False)

        dist = {node: math.inf for node in nodes}
        prev = {node: None for node in nodes}
        visited = set()

        dist[start] = 0
        steps = [
            {
                "desc": f"Inicializar distancias desde {start}",
                "active_nodes": {start},
                "visited_nodes": set(),
            }
        ]

        while len(visited) < len(nodes):
            unvisited = [node for node in nodes if node not in visited]
            if not unvisited:
                break
            current = min(unvisited, key=lambda node: dist[node])
            if dist[current] == math.inf:
                break

            steps.append(
                {
                    "desc": f"Seleccionar nodo con menor distancia: {current}",
                    "active_nodes": {current},
                    "visited_nodes": set(visited),
                }
            )

            visited.add(current)

            for neighbor, weight in adjacency.get(current, []):
                steps.append(
                    {
                        "desc": f"Relajar arista {current}->{neighbor} (peso {weight})",
                        "active_nodes": {current, neighbor},
                        "visited_nodes": set(visited),
                        "active_edges": {self.edge_for_draw(current, neighbor)},
                    }
                )
                alt = dist[current] + weight
                if alt < dist[neighbor]:
                    dist[neighbor] = alt
                    prev[neighbor] = current
                    steps.append(
                        {
                            "desc": f"Actualizar distancia de {neighbor} a {self.format_number(alt)}",
                            "active_nodes": {neighbor},
                            "visited_nodes": set(visited),
                            "active_edges": {self.edge_for_draw(current, neighbor)},
                        }
                    )

        output_lines = [f"Dijkstra desde {start}", "", "Distancias:"]
        for node in nodes:
            output_lines.append(f"{node}: {self.format_number(dist[node])}")
        output_lines.append("")
        output_lines.append("Predecesores:")
        for node in nodes:
            output_lines.append(f"{node} <- {prev[node]}")

        selected_edges = set()
        if end:
            path_nodes = self.reconstruct_path(prev, start, end)
            if path_nodes:
                output_lines.append("")
                output_lines.append(
                    f"Ruta {start} -> {end}: " + " -> ".join(path_nodes)
                )
                output_lines.append(f"Peso total: {self.format_number(dist[end])}")
                for i in range(len(path_nodes) - 1):
                    selected_edges.add(
                        self.edge_for_draw(path_nodes[i], path_nodes[i + 1])
                    )
            else:
                output_lines.append("")
                output_lines.append(f"No hay ruta de {start} a {end}.")

        steps.append(
            {
                "desc": "Resultado final de Dijkstra",
                "visited_nodes": set(visited),
                "selected_edges": selected_edges,
                "output": "\n".join(output_lines),
            }
        )

        self.load_steps(steps)

    def run_floyd(self):
        if not self.graph.nodes:
            messagebox.showerror("Error", "No hay nodos en el grafo.")
            return

        nodes = self.get_sorted_nodes()
        size = len(nodes)
        index = {node: i for i, node in enumerate(nodes)}
        dist = [[math.inf for _ in range(size)] for _ in range(size)]

        for i in range(size):
            dist[i][i] = 0

        for (node1, node2), weight in self.graph.edges.items():
            dist[index[node1]][index[node2]] = weight

        steps = [
            {
                "desc": "Inicializar matriz de distancias",
                "active_nodes": set(),
                "visited_nodes": set(),
            }
        ]

        for k in range(size):
            steps.append(
                {
                    "desc": f"Iteracion k = {nodes[k]}",
                    "active_nodes": {nodes[k]},
                    "pointers": {nodes[k]: "k"},
                }
            )
            for i in range(size):
                for j in range(size):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pointers = self.merge_pointers(
                            [
                                {nodes[i]: "i"},
                                {nodes[j]: "j"},
                                {nodes[k]: "k"},
                            ]
                        )
                        steps.append(
                            {
                                "desc": f"Actualizar dist[{nodes[i]}][{nodes[j]}]",
                                "active_nodes": {nodes[i], nodes[j], nodes[k]},
                                "pointers": pointers,
                            }
                        )

        output = "\n".join(["Floyd (distancias)", "", self.format_matrix(dist, nodes)])

        end = self.end_entry.get().strip()
        result_nodes = set()
        if end and end in index:
            result_nodes.add(end)

        steps.append(
            {
                "desc": "Resultado final de Floyd",
                "result_nodes": result_nodes,
                "output": output,
            }
        )
        self.load_steps(steps)

    def run_floyd_vertices(self):
        if not self.graph.nodes:
            messagebox.showerror("Error", "No hay nodos en el grafo.")
            return

        nodes = self.get_sorted_nodes()
        size = len(nodes)
        index = {node: i for i, node in enumerate(nodes)}
        dist = [[math.inf for _ in range(size)] for _ in range(size)]
        next_node = [[None for _ in range(size)] for _ in range(size)]

        for i in range(size):
            dist[i][i] = 0
            next_node[i][i] = i

        for (node1, node2), weight in self.graph.edges.items():
            i = index[node1]
            j = index[node2]
            dist[i][j] = weight
            next_node[i][j] = j

        steps = [
            {
                "desc": "Inicializar matrices de distancias y vertices",
                "active_nodes": set(),
                "visited_nodes": set(),
            }
        ]

        for k in range(size):
            steps.append(
                {
                    "desc": f"Iteracion k = {nodes[k]}",
                    "active_nodes": {nodes[k]},
                    "pointers": {nodes[k]: "k"},
                }
            )
            for i in range(size):
                for j in range(size):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]
                        pointers = self.merge_pointers(
                            [
                                {nodes[i]: "i"},
                                {nodes[j]: "j"},
                                {nodes[k]: "k"},
                            ]
                        )
                        steps.append(
                            {
                                "desc": f"Actualizar dist y next en [{nodes[i]}][{nodes[j]}]",
                                "active_nodes": {nodes[i], nodes[j], nodes[k]},
                                "pointers": pointers,
                            }
                        )

        next_display = [
            [
                nodes[next_node[i][j]] if next_node[i][j] is not None else None
                for j in range(size)
            ]
            for i in range(size)
        ]

        output_lines = [
            "Floyd guarda vertices",
            "",
            "Distancias:",
            self.format_matrix(dist, nodes),
            "",
            "Next (siguiente):",
            self.format_matrix(next_display, nodes),
        ]

        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        selected_edges = set()

        if start and end and start in index and end in index:
            path = self.reconstruct_path_next(
                next_node, index[start], index[end], nodes
            )
            if path:
                output_lines.append("")
                output_lines.append(f"Ruta {start} -> {end}: " + " -> ".join(path))
                output_lines.append(
                    f"Peso total: {self.format_number(dist[index[start]][index[end]])}"
                )
                for i in range(len(path) - 1):
                    selected_edges.add(self.edge_for_draw(path[i], path[i + 1]))
            else:
                output_lines.append("")
                output_lines.append(f"No hay ruta de {start} a {end}.")

        steps.append(
            {
                "desc": "Resultado final de Floyd con vertices",
                "selected_edges": selected_edges,
                "output": "\n".join(output_lines),
            }
        )
        self.load_steps(steps)

    def run_warshall(self):
        if not self.graph.nodes:
            messagebox.showerror("Error", "No hay nodos en el grafo.")
            return

        nodes = self.get_sorted_nodes()
        size = len(nodes)
        index = {node: i for i, node in enumerate(nodes)}
        reach = [[False for _ in range(size)] for _ in range(size)]

        for i in range(size):
            reach[i][i] = True

        for node1, node2 in self.graph.edges.keys():
            reach[index[node1]][index[node2]] = True

        steps = [
            {
                "desc": "Inicializar matriz de alcanzabilidad",
                "active_nodes": set(),
                "visited_nodes": set(),
            }
        ]

        for k in range(size):
            steps.append(
                {
                    "desc": f"Iteracion k = {nodes[k]}",
                    "active_nodes": {nodes[k]},
                    "pointers": {nodes[k]: "k"},
                }
            )
            for i in range(size):
                for j in range(size):
                    if reach[i][k] and reach[k][j] and not reach[i][j]:
                        reach[i][j] = True
                        pointers = self.merge_pointers(
                            [
                                {nodes[i]: "i"},
                                {nodes[j]: "j"},
                                {nodes[k]: "k"},
                            ]
                        )
                        steps.append(
                            {
                                "desc": f"Marcar alcance {nodes[i]} -> {nodes[j]}",
                                "active_nodes": {nodes[i], nodes[j], nodes[k]},
                                "pointers": pointers,
                            }
                        )

        output = "\n".join(
            ["Warshall (alcanzabilidad)", "", self.format_matrix(reach, nodes)]
        )
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        result_nodes = set()
        if start in index and end in index:
            if reach[index[start]][index[end]]:
                result_nodes.add(end)

        steps.append(
            {
                "desc": "Resultado final de Warshall",
                "result_nodes": result_nodes,
                "output": output,
            }
        )
        self.load_steps(steps)

    def run_prim(self):
        if not self.graph.nodes:
            messagebox.showerror("Error", "No hay nodos en el grafo.")
            return
        if not self.graph.edges:
            messagebox.showerror("Error", "No hay aristas en el grafo.")
            return

        start = self.start_entry.get().strip()
        if not start:
            messagebox.showerror("Error", "Debe indicar el nodo inicio.")
            return
        if start not in self.graph.nodes:
            messagebox.showerror("Error", "El nodo inicio no existe.")
            return

        nodes = self.get_sorted_nodes()
        adjacency = self.build_adjacency(undirected=True)
        visited = {start}
        selected_edges = set()
        total_weight = 0

        steps = [
            {
                "desc": f"Iniciar arbol con {start}",
                "active_nodes": {start},
                "visited_nodes": set(visited),
            }
        ]

        while len(visited) < len(nodes):
            best_edge = None
            best_weight = math.inf
            for node in visited:
                for neighbor, weight in adjacency.get(node, []):
                    if neighbor in visited:
                        continue
                    if weight < best_weight:
                        best_weight = weight
                        best_edge = (node, neighbor)

            if best_edge is None:
                break

            node, neighbor = best_edge
            visited.add(neighbor)
            draw_edge = self.edge_for_draw(node, neighbor)
            selected_edges.add(draw_edge)
            total_weight += best_weight

            steps.append(
                {
                    "desc": f"Agregar arista {node}-{neighbor} (peso {best_weight})",
                    "active_nodes": {node, neighbor},
                    "visited_nodes": set(visited),
                    "selected_edges": set(selected_edges),
                    "active_edges": {draw_edge},
                }
            )

        output_lines = ["Prim (N)", "", "Aristas seleccionadas:"]
        for node1, node2 in selected_edges:
            weight = self.graph.edges.get((node1, node2))
            if weight is None:
                weight = self.graph.edges.get((node2, node1))
            output_lines.append(
                f"{node1} - {node2} (peso {self.format_number(weight)})"
            )
        output_lines.append("")
        output_lines.append(f"Peso total: {self.format_number(total_weight)}")

        steps.append(
            {
                "desc": "Resultado final de Prim",
                "selected_edges": set(selected_edges),
                "visited_nodes": set(visited),
                "output": "\n".join(output_lines),
            }
        )
        self.load_steps(steps)

    def run_kruskal(self):
        if not self.graph.nodes:
            messagebox.showerror("Error", "No hay nodos en el grafo.")
            return
        if not self.graph.edges:
            messagebox.showerror("Error", "No hay aristas en el grafo.")
            return

        nodes = self.get_sorted_nodes()
        edges = self.get_undirected_edges()
        edges.sort(key=lambda item: item[2])

        parent = {node: node for node in nodes}
        rank = {node: 0 for node in nodes}

        def find(node):
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        def union(node1, node2):
            root1 = find(node1)
            root2 = find(node2)
            if root1 == root2:
                return False
            if rank[root1] < rank[root2]:
                parent[root1] = root2
            elif rank[root1] > rank[root2]:
                parent[root2] = root1
            else:
                parent[root2] = root1
                rank[root1] += 1
            return True

        selected_edges = set()
        total_weight = 0

        steps = [
            {
                "desc": "Ordenar aristas por peso",
                "active_nodes": set(),
                "visited_nodes": set(),
            }
        ]

        for node1, node2, weight in edges:
            draw_edge = self.edge_for_draw(node1, node2)
            steps.append(
                {
                    "desc": f"Evaluar arista {node1}-{node2} (peso {weight})",
                    "active_nodes": {node1, node2},
                    "active_edges": {draw_edge},
                    "selected_edges": set(selected_edges),
                }
            )
            if union(node1, node2):
                selected_edges.add(draw_edge)
                total_weight += weight
                steps.append(
                    {
                        "desc": f"Agregar arista {node1}-{node2}",
                        "active_nodes": {node1, node2},
                        "selected_edges": set(selected_edges),
                        "active_edges": {draw_edge},
                    }
                )
            if len(selected_edges) == len(nodes) - 1:
                break

        output_lines = ["Kruskal (N)", "", "Aristas seleccionadas:"]
        for node1, node2 in selected_edges:
            weight = self.graph.edges.get((node1, node2))
            if weight is None:
                weight = self.graph.edges.get((node2, node1))
            output_lines.append(
                f"{node1} - {node2} (peso {self.format_number(weight)})"
            )
        output_lines.append("")
        output_lines.append(f"Peso total: {self.format_number(total_weight)}")

        steps.append(
            {
                "desc": "Resultado final de Kruskal",
                "selected_edges": set(selected_edges),
                "output": "\n".join(output_lines),
            }
        )
        self.load_steps(steps)

    # =========================
    # RECONSTRUCCION DE RUTAS
    # =========================
    def reconstruct_path(self, prev, start, end):
        path = []
        current = end
        while current is not None:
            path.append(current)
            if current == start:
                break
            current = prev[current]
        if not path or path[-1] != start:
            return []
        path.reverse()
        return path

    def reconstruct_path_next(self, next_node, start_idx, end_idx, nodes):
        if next_node[start_idx][end_idx] is None:
            return []
        path = [nodes[start_idx]]
        current = start_idx
        guard = 0
        while current != end_idx:
            current = next_node[current][end_idx]
            if current is None:
                return []
            path.append(nodes[current])
            guard += 1
            if guard > len(nodes):
                return []
        return path


# ======================================
# EJECUCIÓN
# ======================================
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
