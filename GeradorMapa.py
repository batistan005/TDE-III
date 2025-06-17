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

   #Gerar Cachoeira e Caverna v
#-----------------------------------------------------------------------------------------------------------------------------------------
    bordas = []
    for x,y in montanhas_totais:
        for vx,vy in get_vizinhos((x,y),largura,altura):
            if mapa[(vx,vy)] is None:
                bordas.append((vx,vy))
    
    pos_cachoeira = random.choice(bordas)
    bordas.remove(pos_cachoeira)

    pos_caverna = random.choice(bordas)

    mapa[pos_cachoeira] = Terreno(pos_cachoeira, "Cachoeira")
    mapa[pos_caverna] = Terreno(pos_caverna, "Caverna")
    #imprimir_mapa_texto_com_grade_e_cores(mapa, MAPA_LARGURA, MAPA_ALTURA, LARGURA_CELULA)
#-----------------------------------------------------------------------------------------------------------------------------------------
    #Gerar Cachoeira e Caverna ^

   #Gerar Rio v
#-----------------------------------------------------------------------------------------------------------------------------------------
    direcoes_rio = {}

    for x, y in get_vizinhos(pos_cachoeira, largura, altura):
        if mapa[(x, y)] is None:
            dx = x - pos_cachoeira[0]
            dy = y - pos_cachoeira[1]
            direcoes_rio[(x, y)] = [0, (dx, dy)] 

            nx, ny = x, y
            while 0 <= nx < largura and 0 <= ny < altura and mapa[(nx, ny)] is None:
                direcoes_rio[(x, y)][0] += 1
                nx += dx
                ny += dy

    base_rio = max(direcoes_rio, key=direcoes_rio.get)
    curva = random.randint(0,1)
    direcao = direcoes_rio[base_rio][1]
    num_rio = direcoes_rio[base_rio][0]
    rios_totais = [base_rio]
    mapa[base_rio] = Terreno(base_rio, "Rio")
    min_rios = round(num_rio/2)

    x, y = base_rio
    dx, dy = direcao
    print(dx,dy)
    print(curva)

    while len(rios_totais) < num_rio:
        if len(rios_totais) >= min_rios:
            if curva == 0:
                oldx = dx
                dx = dy
                dy = oldx
            elif curva == 1:
                oldx = dx
                dx = -dy
                dy = -oldx
            curva = 2
        x += dx
        y += dy
        if not (0 <= x < largura and 0 <= y < altura):
            break
        elif curva == 2:
            num_rio += 1
        if mapa[(x, y)] is not None:
            break
        mapa[(x, y)] = Terreno((x, y), "Rio")
        rios_totais.append((x, y))


    #imprimir_mapa_texto_com_grade_e_cores(mapa, MAPA_LARGURA, MAPA_ALTURA, LARGURA_CELULA)
#-----------------------------------------------------------------------------------------------------------------------------------------
    #Gerar Rio ^

   #Gerar Planicie v
#-----------------------------------------------------------------------------------------------------------------------------------------
    while True:
        planicie_y = (random.randint(0,8))
        planicie_x = (random.randint(0,8))

        if mapa[(planicie_x,planicie_y)] == None:
            mapa[(planicie_x,planicie_y)] = Terreno((planicie_x,planicie_y), "Planície")
            break
        

    planicies_totais = [(planicie_x, planicie_y)]
    num_planicies = random.randint(9,14)

    while num_planicies > len(planicies_totais):
        base_planicie = random.choice(planicies_totais)
        novas_planicies = get_vizinhos(base_planicie, largura, altura)

        for x,y in novas_planicies:
            if mapa[(x,y)] == None:
                mapa[(x,y)] = Terreno((x,y), "Planície")
                planicies_totais.append((x,y))
                break
    #imprimir_mapa_texto_com_grade_e_cores(mapa, MAPA_LARGURA, MAPA_ALTURA, LARGURA_CELULA)
#-----------------------------------------------------------------------------------------------------------------------------------------
    #Gerar Planicie ^