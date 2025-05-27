
import tkinter as tk
from tkinter import messagebox
import pickle
import numpy as np
import random
from collections import defaultdict

# === ENTORNO DEL JUEGO ===
class Connect4Env:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.reset()

    def reset(self):
        self.board = np.zeros((self.rows, self.cols), dtype=int)
        self.done = False
        self.winner = None
        self.turn = -1  # Humano comienza
        return self._get_state()

    def _get_state(self):
        return tuple(map(tuple, self.board))

    def get_valid_actions(self):
        return [c for c in range(self.cols) if self.board[0, c] == 0]

    def step(self, action):
        if self.done or self.board[0, action] != 0:
            return self._get_state(), -10, True  # penalización por acción inválida

        for r in reversed(range(self.rows)):
            if self.board[r, action] == 0:
                self.board[r, action] = self.turn
                break

        if self._check_win(self.turn):
            self.done = True
            self.winner = self.turn
            return self._get_state(), 1 if self.turn == 1 else -1, True

        if np.all(self.board != 0):
            self.done = True
            return self._get_state(), 0, True  # empate

        self.turn *= -1
        return self._get_state(), 0, False

    def _check_win(self, player):
        for c in range(self.cols - 3):
            for r in range(self.rows):
                if all(self.board[r, c+i] == player for i in range(4)):
                    return True
        for c in range(self.cols):
            for r in range(self.rows - 3):
                if all(self.board[r+i, c] == player for i in range(4)):
                    return True
        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
                if all(self.board[r+i, c+i] == player for i in range(4)):
                    return True
        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if all(self.board[r-i, c+i] == player for i in range(4)):
                    return True
        return False

# === CARGAR AGENTE ENTRENADO ===
with open("agente_q_table.pkl", "rb") as f:
    Q = defaultdict(lambda: np.zeros(7), pickle.load(f))

def choose_action(state, valid_actions):
    q_values = Q[state]
    max_value = float('-inf')
    best_actions = []
    for a in valid_actions:
        if q_values[a] > max_value:
            best_actions = [a]
            max_value = q_values[a]
        elif q_values[a] == max_value:
            best_actions.append(a)
    return random.choice(best_actions)

# === INTERFAZ DE JUEGO HUMANO VS AGENTE ===
def jugar_vs_agente():
    env = Connect4Env()
    state = env.reset()

    root = tk.Tk()
    root.title("Cuatro en Raya - Tú vs Agente")

    def actualizar_tablero():
        for r in range(env.rows):
            for c in range(env.cols):
                valor = env.board[r][c]
                texto = " "
                color = "white"
                if valor == 1:
                    texto = "A"
                    color = "lightblue"
                elif valor == -1:
                    texto = "Tú"
                    color = "lightgreen"
                casillas[r][c].config(text=texto, bg=color)

    def accion(columna):
        nonlocal state
        if env.done:
            return

        if columna not in env.get_valid_actions():
            messagebox.showwarning("¡Acción invalida!", "Esa columna ya está llena.")
            return

        # Turno del humano
        state, _, done = env.step(columna)
        actualizar_tablero()

        if done:
            mostrar_resultado()
            return

        # Turno del agente
        action_agente = choose_action(state, env.get_valid_actions())
        state, _, done = env.step(action_agente)
        actualizar_tablero()

        if done:
            mostrar_resultado()

    def mostrar_resultado():
        if env.winner == 1:
            messagebox.showinfo("Resultado", "¡Gano el Agente!")
        elif env.winner == -1:
            messagebox.showinfo("Resultado", "¡Ganaste tu!")
        else:
            messagebox.showinfo("Resultado", "¡Empate!")
        root.quit()

    botones = []
    for c in range(env.cols):
        btn = tk.Button(root, text=f"↓ {c}", command=lambda col=c: accion(col))
        btn.grid(row=0, column=c)
        botones.append(btn)

    casillas = []
    for r in range(env.rows):
        fila = []
        for c in range(env.cols):
            label = tk.Label(root, text=" ", width=6, height=2, borderwidth=2, relief="ridge", bg="white")
            label.grid(row=r+1, column=c)
            fila.append(label)
        casillas.append(fila)

    actualizar_tablero()
    root.mainloop()

if __name__ == "__main__":
    jugar_vs_agente()
