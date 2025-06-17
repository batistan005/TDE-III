# ForestGame.py
import os
import sys
import random
import time
from rich.console import Console

# Importa o nosso módulo de geração de mapa
import GeradorMapa

# --- Constantes e Configurações do Jogo ---
console = Console()

MSG_INICIAL = """Você acorda desorientado, no meio de uma floresta densa e desconhecida.
Seu objetivo é claro: encontrar uma maneira de sair deste lugar.
Explore, colete recursos e sobreviva. Boa sorte."""

MAX_ATRIBUTOS = 100
CUSTO_PA = {"Madeira": 5, "Pedra": 2}
CUSTO_CABANA = {"Madeira": 50, "Pedra": 20} # Custo para construir uma cabana