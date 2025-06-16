import random
from rich.console import Console
from rich.text import Text

console = Console()

RECURSOS_TIPO = {
    "Floresta": {"Comida": 2, "Água": 0, "Itens": 0, "Madeira": 3, "Pedra": 0, "Animais": 1},
    "Rio": {"Comida": 2, "Água": 3, "Itens": 0, "Madeira": 1, "Pedra": 0, "Animais": 1},
    "Planície": {"Comida": 1, "Água": 0, "Itens": 1, "Madeira": 1, "Pedra": 1, "Animais": 2},
    "Montanha": {"Comida": 0, "Água": 0, "Itens": 1, "Madeira": 0, "Pedra": 4, "Animais": 1},
    "Caverna": {"Comida": 0, "Água": 1, "Itens": 3, "Madeira": 0, "Pedra": 2, "Animais": 0},
    "Cachoeira": {"Comida": 0, "Água": 3, "Itens": 2, "Madeira": 0, "Pedra": 1, "Animais": 1},
}

CORES_TERRENO = {
    "Floresta": "dark_green",
    "Planície": "spring_green2",
    "Rio": "blue1",
    "Caverna": "bright_magenta",
    "Montanha": "bright_red",
    "Cachoeira": "yellow2",
    "??": "white" # Para tipos desconhecidos/erros
}

ABREVIACOES_TERRENO = {
    "Floresta": "FLO",
    "Rio": "RIO",
    "Planície": "PLA",
    "Montanha": "MON",
    "Caverna": "CAV",
    "Cachoeira": "CAC",
}

class Terreno:
    def __init__(self, posicao, tipo):
        self.posicao = posicao
        self.tipo = tipo
        self.recursos = self._gerar_recursos(self.tipo)
        self.cabana = False
        self.saida = False
        self.tempo_travessia = self._definir_tempo(self.tipo)

    def _gerar_recursos(self, tipo_atual):
        recursos_final = {}
        for recurso, valor_base in RECURSOS_TIPO[tipo_atual].items():
            # Gera recursos com alguma variação, de 1 a 3 vezes o valor base
            recursos_final[recurso] = random.randint(1, 3) * valor_base
        return recursos_final
    
    def _definir_tempo(self, tipo):
        match tipo:
            case "Planície" | "Rio" | "Caverna":
                tempo = 1
            case "Floresta" | "Cachoeira":
                tempo = 2
            case "Montanha":
                tempo = 3
        return tempo

    def get_abreviacao(self):
        # Retorna a abreviação para exibição no mapa
        return ABREVIACOES_TERRENO.get(self.tipo, "???")

    def get_cor(self):
        # Retorna a cor Rich para o tipo de terreno
        if self.saida == True:
            return("orange")
        else:
            return CORES_TERRENO.get(self.tipo, "white")

MAPA_LARGURA = 9 
MAPA_ALTURA = 9
LARGURA_CELULA = 5

def get_vizinhos(posicao, largura, altura):
    x,y = posicao
    vizinhos = []
    for tx,ty in [(1,0),(-1,0),(0,1),(0,-1)]:
        vx,vy = x + tx, y+ty

        if 0 <= vx < largura and 0 <= vy < altura:
            vizinhos.append((vx,vy))
    return vizinhos

def gerar_mapa(largura,altura):
    mapa = {}

    #Preecher posições do mapa com vazio
    for y in range(altura):
        for x in range(largura):
            mapa[(x,y)] = None

   #Gerar Montanha v
#-----------------------------------------------------------------------------------------------------------------------------------------
    montanha_y = (random.randint(0,1)) * (altura - 1)
    montanha_x = (random.randint(0,1)) * (largura - 1)
    mapa[(montanha_x,montanha_y)] = Terreno((montanha_x,montanha_y), "Montanha")

    montanhas_totais = [(montanha_x, montanha_y)]
    num_montanhas = random.randint(6,9)

    while num_montanhas > len(montanhas_totais):
        base_montanha = random.choice(montanhas_totais)
        novas_montanhas = get_vizinhos(base_montanha, largura, altura)

        for x,y in novas_montanhas:
            if mapa[(x,y)] == None:
                mapa[(x,y)] = Terreno((x,y), "Montanha")
                montanhas_totais.append((x,y))
                #imprimir_mapa_texto_com_grade_e_cores(mapa, MAPA_LARGURA, MAPA_ALTURA, LARGURA_CELULA)
                break
    #imprimir_mapa_texto_com_grade_e_cores(mapa, MAPA_LARGURA, MAPA_ALTURA, LARGURA_CELULA)
#-----------------------------------------------------------------------------------------------------------------------------------------
    #Gerar Montanha ^