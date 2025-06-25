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

def salvar_resultado(player, partida, status, motivo=None):
    """Grava (ou acrescenta) o resultado da partida em resultados.json."""
    registro = {
        "status": status,                    # "vitória" ou "derrota"
        "dias_sobrevividos": partida.dia,
        "motivo": motivo,                    # None quando vencer
        "mochila": player.mochila.copy(),
        "tem_cabana": player.tem_cabana
    }

    arquivo = "resultados.json"

    # Se já existe, carrega lista; se não, começa vazia
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if not isinstance(dados, list):
                dados = [dados]
    except FileNotFoundError:
        dados = []

    # Adiciona novo registro e salva de volta
    dados.append(registro)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# --- Classes do Jogo ---

class Jogador:
    """Define atributos e ações do jogador."""
    def __init__(self, vida, energia, fome):
        self.vida = vida
        self.energia = energia
        self.fome = fome
        self.mochila = {}
        self.terreno_atual = None
        self.jogo = None
        self.tem_mapa = False
        self.tem_cabana = False

    def andar(self):
        print("Qual direção pretende seguir?")
        print("[1] Norte (Cima)")
        print("[2] Sul (Baixo)")
        print("[3] Leste (Direita)")
        print("[4] Oeste (Esquerda)")
        print("[5] Voltar")

        direcao_map = {1: (-1, 0), 2: (1, 0), 3: (0, 1), 4: (0, -1)}
        escolha = self.jogo.verifica_escolha(1, 5)

        if escolha == 5:
            return

        soma_y, soma_x = direcao_map[escolha]
        # A posição no mapa é (x, y), mas nossa entrada é (y, x) visualmente
        pos_atual_x, pos_atual_y = self.terreno_atual.posicao
        nova_pos = (pos_atual_x + soma_x, pos_atual_y + soma_y)

        if nova_pos in self.jogo.mapa:
            self.terreno_atual = self.jogo.mapa[nova_pos]
            custo_energia = round(self.terreno_atual.tempo_travessia * 4.5)
            self.energia -= custo_energia
            self.fome -= round(custo_energia / 2)
            self.jogo.passar_horas(self.terreno_atual.tempo_travessia)
            self.jogo.mensagem = f"Você chegou em: {self.terreno_atual.tipo}."
        else:
            print("Você não pode seguir por essa direção. Há um limite na floresta.")
            time.sleep(1)

    def explorar(self):
        print(f"Explorando {self.terreno_atual.tipo}...")
        time.sleep(1)
        self.energia -= round(self.terreno_atual.tempo_travessia * 5)
        self.fome -= round(self.terreno_atual.tempo_travessia * 2)

        recursos_encontrados = False
        # A classe Terreno está em GeradorMapa, então usamos os recursos de lá
        for recurso, valor in self.terreno_atual.recursos.items():
            if valor > 0:
                recursos_encontrados = True
                print(f"  - {valor}x {recurso}")
                if recurso not in ["Animais", "Água"]:
                    self.mochila[recurso] = self.mochila.get(recurso, 0) + valor
                self.terreno_atual.recursos[recurso] = 0
        
        if not recursos_encontrados:
            print("Você não encontrou nada de novo aqui.")

        if self.terreno_atual.tipo == "Caverna" and not self.tem_mapa:
            self.tem_mapa = True
            self.mochila["Mapa"] = 1
            self.jogo.mensagem = "Nas profundezas da caverna, você encontra uma caixa estranha. Dentro, um mapa!"
        
        self.jogo.passar_horas(self.terreno_atual.tempo_travessia)

    def alimentar(self):
        if not "Comida" in self.mochila.keys():
            print("Você não tem nada para comer.")
            time.sleep(1)
            return
        else:
            quantidade = int(input("Quanto você quer comer?"))
            if quantidade > self.mochila["Comida"]:
                print("Você não tem comida o suficiente pra isso!")
            elif quantidade < 1:
                print("Valor inválido!")
            else:
                self.mochila["Comida"] -= quantidade
                self.fome = min(MAX_ATRIBUTOS, self.fome + (3 * quantidade))
                self.jogo.mensagem = f"Você comeu e se sente um pouco melhor."
        
        # Chance de passar mal
        chance = random.randint(1,6) * round(quantidade / 10)
        if chance > 6 :
            self.vida -= (self.vida * 0.15)
            self.jogo.mensagem = f"A comida não lhe caiu bem! Você se sente enjoado e perdeu vida."
            time.sleep(1)

    def construir_cabana(self):
        if self.terreno_atual.tipo not in ["Planície", "Floresta", "Rio"]:
            print("Você só pode construir uma cabana em um terreno plano e seguro (Planície, Floresta ou Rio).")
            time.sleep(1)
            return

        madeira_necessaria = CUSTO_CABANA["Madeira"]
        pedra_necessaria = CUSTO_CABANA["Pedra"]
        madeira_atual = self.mochila.get("Madeira", 0)
        pedra_atual = self.mochila.get("Pedra", 0)

        if madeira_atual >= madeira_necessaria and pedra_atual >= pedra_necessaria:
            self.mochila["Madeira"] -= madeira_necessaria
            self.mochila["Pedra"] -= pedra_necessaria
            self.energia -= 50
            self.fome -= 20
            self.tem_cabana = True
            self.jogo.passar_horas(8)
            self.jogo.mensagem = "Com muito esforço, você constrói uma cabana! Agora tem um lugar seguro para descansar."
        else:
            print("Você não tem recursos suficientes para construir uma cabana.")
            print(f"Falta: {max(0, madeira_necessaria - madeira_atual)} Madeira, {max(0, pedra_necessaria - pedra_atual)} Pedra")
            time.sleep(2)

    def descansar(self):
        print("Quanto tempo quer descansar (1-8 horas)?")
        tempo_descanso = self.jogo.verifica_escolha(1, 8, "Você não pode descansar mais que 8 horas!")
        
        if not self.tem_cabana and self.terreno_atual.tipo != "Caverna" and (random.randint(1, 10) * round(tempo_descanso / 10)) > 8:
            print("Um som te acorda! Você foi atacado por um animal enquanto dormia!")
            self.vida -= random.randint(30, 70)
            time.sleep(1)
            if self.vida <= 0:
                self.jogo.game_over("Você não sobreviveu ao ataque...")
            return

        if self.tem_cabana:
            print("Você descansa seguro em sua cabana.")

        print(f"Você descansou por {tempo_descanso} hora(s).")
        self.energia = min(MAX_ATRIBUTOS, self.energia + tempo_descanso * 10)
        self.fome = max(0, self.fome - tempo_descanso * 2)
        self.vida = min(MAX_ATRIBUTOS, self.vida + tempo_descanso * 2)
        self.jogo.passar_horas(tempo_descanso)

    def construir_pa(self):
        print(f"Construindo Pá... (Custo: {CUSTO_PA['Madeira']} Madeira, {CUSTO_PA['Pedra']} Pedra)")
        time.sleep(1)
        if self.mochila.get("Madeira", 0) >= CUSTO_PA['Madeira'] and self.mochila.get("Pedra", 0) >= CUSTO_PA['Pedra']:
            self.mochila["Madeira"] -= CUSTO_PA['Madeira']
            self.mochila["Pedra"] -= CUSTO_PA['Pedra']
            self.mochila["Pá"] = 1
            self.energia -= 15
            self.fome -= 5
            self.jogo.passar_horas(2)
            print("Você construiu uma Pá com sucesso!")
        else:
            print("Você não tem recursos suficientes.")
    
    def cavar(self):
        print("Você usa a pá e começa a cavar na terra fofa...")
        self.energia -= 25
        self.fome -= 10
        self.jogo.passar_horas(3)
        time.sleep(2)
        if terreno_atual.saida == True:
            print("Após algum esforço, sua pá atinge algo metálico. É uma escotilha!")
            time.sleep(2)
            print("Você abre a escotilha e encontra um portal brilhante. Sem hesitar, você pula.")
            time.sleep(2)
            self.jogo.vitoria()
        else:
            print("Você cava mas não encontra nada! Parabéns...")
            return

    def abrir_mochila(self):
        print("\n--- Mochila ---")
        if not self.mochila:
            print("Sua mochila está vazia.")
        else:
            for item, quantidade in self.mochila.items():
                if quantidade > 0:
                    print(f"- {item}: {quantidade}")
        print("---------------")
        input("Pressione Enter para voltar...")

    def ver_mapa(self):
        if self.tem_mapa:
            print(f"O mapa revela que a saída está nas coordenadas: X={self.jogo.saida_pos[0]}, Y={self.jogo.saida_pos[1]}")
            GeradorMapa.imprimir_mapa_texto_com_grade_e_cores(self.jogo.mapa, 9, 9, 5)
            input("Pressione Enter para voltar...")
        else:
            print("Você não tem um mapa.")

    def verificar_status(self):
        if self.energia <= 0:
            print("Você desmaiou de cansaço!")
            time.sleep(1)
            self.energia = 0
            if self.terreno_atual.tipo == "Caverna" or self.tem_cabana:
                print("Você desmaiou em um lugar seguro que te protegeu enquanto você estava desacordado.")
                self.energia += 40
                self.jogo.passar_horas(8)
            else:
                if random.randint(1, 4) == 1:
                    self.jogo.game_over("Animais selvagens te encontraram enquanto você estava vulnerável.")
                else:
                    print("Por sorte, nada aconteceu. Você acorda se sentindo fraco.")
                    self.energia += 30
                    self.jogo.passar_horas(8)
        elif self.energia <= 30:
            print("\nCuidado sua energia está baixa!")
            time.sleep(2)
        
        if self.fome <= 0:
            print("Você está morrendo de fome! Sua vida está diminuindo...")
            self.fome = 0
            self.vida -= 15
        
        self.vida = min(MAX_ATRIBUTOS, self.vida)
        self.energia = min(MAX_ATRIBUTOS, self.energia)
        if self.vida <= 0:
            self.jogo.game_over("Sua jornada termina aqui.")


class Partida:
    """Controla o fluxo da partida, eventos, e o estado do jogo."""
    def __init__(self, player):
        self.dia = 1
        self.hora = 6
        self.player = player
        self.mensagem = MSG_INICIAL
        
        # Aqui é a mágica: chamamos a função do outro arquivo para obter o mapa
        self.mapa, self.saida_pos = GeradorMapa.gerar_mapa(GeradorMapa.MAPA_LARGURA, GeradorMapa.MAPA_ALTURA)
        
        # Define a posição inicial do jogador
        while True:
            start_pos = (random.randint(0, GeradorMapa.MAPA_LARGURA - 1), random.randint(0, GeradorMapa.MAPA_ALTURA - 1))
            if self.mapa[start_pos].tipo in ["Planície", "Floresta"]:
                self.player.terreno_atual = self.mapa[start_pos]
                break
    
    def hud(self):
        if self.mensagem:
            console.print(f"[italic yellow]{self.mensagem}[/italic yellow]\n")
            self.mensagem = ""
            time.sleep(1)

        vida_cor = "green" if self.player.vida > 30 else "red"
        energia_cor = "green" if self.player.energia > 30 else "yellow"
        fome_cor = "green" if self.player.fome > 30 else "yellow"

        console.print(f"Dia: {self.dia} | Hora: {self.hora:02d}:00")
        console.print(f"Vida: [{vida_cor}]{self.player.vida}/{MAX_ATRIBUTOS}[/{vida_cor}] | "
                      f"Energia: [{energia_cor}]{self.player.energia}/{MAX_ATRIBUTOS}[/{energia_cor}] | "
                      f"Fome: [{fome_cor}]{self.player.fome}/{MAX_ATRIBUTOS}[/{fome_cor}]")
        
        pos = self.player.terreno_atual.posicao
        terreno_tipo = self.player.terreno_atual.tipo
        terreno_cor = GeradorMapa.CORES_TERRENO.get(terreno_tipo, "white")
        console.print(f"Local: [{terreno_cor}]{terreno_tipo}[/{terreno_cor}] | Coordenadas: X:{pos[0]} Y:{pos[1]}\n")

        # Menu de Ações
        acoes = {
            '1': {'texto': 'Andar', 'acao': self.player.andar},
            '2': {'texto': 'Explorar Terreno', 'acao': self.player.explorar},
            '3': {'texto': 'Descansar', 'acao': self.player.descansar},
            '4': {'texto': 'Abrir Mochila', 'acao': self.player.abrir_mochila},
            '5': {'texto': 'Comer','acao': self.player.alimentar}
        }
        proximo_indice = 6

        if not self.player.tem_cabana:
            madeira_necessaria = CUSTO_CABANA["Madeira"]
            pedra_necessaria = CUSTO_CABANA["Pedra"]
            madeira_atual = self.player.mochila.get("Madeira", 0)
            pedra_atual = self.player.mochila.get("Pedra", 0)
            
            texto_cabana = f"Construir Cabana ({madeira_atual}/{madeira_necessaria}M, {pedra_atual}/{pedra_necessaria}P)"
            acoes[str(proximo_indice)] = {'texto': texto_cabana, 'acao': self.player.construir_cabana}
            proximo_indice += 1
            
        if "Pá" not in self.player.mochila:
            acoes[str(proximo_indice)] = {'texto': f"Construir Pá ({CUSTO_PA['Madeira']}M, {CUSTO_PA['Pedra']}P)", 'acao': self.player.construir_pa}
            proximo_indice += 1
        if self.player.tem_mapa:
            acoes[str(proximo_indice)] = {'texto': 'Ver Posição da Saída', 'acao': self.player.ver_mapa}
            proximo_indice += 1
        if self.player.terreno_atual.posicao == self.saida_pos and "Pá" in self.player.mochila and self.player.tem_mapa:
             acoes[str(proximo_indice)] = {'texto': 'CAVAR!', 'acao': self.player.cavar}
        
        for key, value in acoes.items():
            print(f"[{key}] {value['texto']}")
        
        escolha = self.verifica_escolha(1, len(acoes))
        acoes[str(escolha)]['acao']()

    def passar_horas(self, horas):
        self.hora += horas
        if self.hora >= 24:
            self.hora -= 24
            self.dia += 1
            self.mensagem = f"Um novo dia começa. Já se passaram {self.dia} dias."
        if random.randint(1, 10) == 1:
            self.evento_aleatorio()

    def evento_aleatorio(self):
        eventos = [
            "Você escuta um som de disparo ao leste. Talvez seja melhor não ir pra lá por enquanto.",
            "Você encontra um cogumelo selvagem.",
            "Um barulho te assusta!.",
            "Você tropeça em uma raiz e cai. Por sorte, não se machucou, mas perdeu um pouco de energia."
        ]
        evento_escolhido = random.choice(eventos)
        console.print(f"\n[italic cyan]{evento_escolhido}[/italic cyan]")
        if "tropeça" in evento_escolhido:
            self.player.energia -= 10

        elif "cogumelo" in evento_escolhido:
            console.print(f"\n[italic cyan][1] Sim[/italic cyan]")
            console.print(f"[italic cyan][2] Não[/italic cyan]")
            console.print(f"[italic cyan]Deseja come-lo? [/italic cyan]")
            choice = int(input(f""))
            while choice < 1 or choice > 2:
                console.print(f"\n[italic cyan]Escolha invalida![/italic cyan]")
                choice = int(input(f""))
            if choice == 1 and random.randint(1,2) > 1:
                print("Você não sente nada demais...")
                time.sleep(2)
                self.game_over("Morto por cogumelo venenoso!")
            elif choice == 1:
                print("Você recuperou todos os status ao máximo!")
                self.player.energia = MAX_ATRIBUTOS
                self.player.vida = MAX_ATRIBUTOS
                self.player.fome = MAX_ATRIBUTOS
            else:
                print("Você apenas deixa a planta do jeito que encontrou!")
            
        elif "barulho" in evento_escolhido:
            console.print(f"\n[italic cyan][1] Sim[/italic cyan]")
            console.print(f"[italic cyan][2] Não[/italic cyan]")
            console.print(f"[italic cyan]Deseja investigar o barulho?[/italic cyan]")
            choice = int(input(f""))
            while choice < 1 or choice > 2:
                console.print(f"[italic cyan]Escolha invalida![/italic cyan]")
                choice = int(input(f""))
            if choice == 1:
                console.print(f"[italic cyan]Era apenas um siri fazendo barra. Você fica feliz por ve-lo dedicado ao exercicio[/italic cyan]")
                console.print(f"\n[italic cyan][1] Sim[/italic cyan]")
                console.print(f"[italic cyan][2] Não[/italic cyan]")
                console.print(f"[italic cyan]Assustar o siri?[/italic cyan]")
                choice = int(input(""))
                while choice < 1 or choice > 2:
                    console.print(f"\n[italic cyan]Escolha invalida![/italic cyan]")
                    choice = int(input(f""))
                if choice == 1:
                    self.game_over("Nunca assuste o siri...")
                else:
                   console.print(f"\n[italic cyan]Você apenas o deixa continuar a barra normal![/italic cyan]")

        time.sleep(2)

    def verifica_escolha(self, low, upper, display="Opção inválida."):
        while True:
            try:
                escolha = int(input("\nSua escolha: "))
                if low <= escolha <= upper:
                    return escolha
                else:
                    print(display)
            except ValueError:
                print("Por favor, insira um número válido.")

    def game_over(self, motivo):
        os.system('cls')
        console.print("\n[bold red]VOCÊ PERDEU[/bold red]")
        console.print(motivo)
        console.print(f"Você sobreviveu por {self.dia} dia(s).")
        salvar_resultado(self.player, self, status="derrota", motivo=motivo)
        print("Arquivo JSON gerado!")
        sys.exit()
    
    def vitoria(self):
        os.system('cls')
        console.print("\n[bold green]VOCÊ ESCAPOU![/bold green]")
        console.print("Você emerge em um lugar familiar, a floresta ficou para trás.")
        console.print(f"Você sobreviveu por {self.dia} dia(s) e encontrou o caminho de casa!")
        salvar_resultado(self.player, self, status="vitória")
        print("Arquivo JSON gerado!")
        sys.exit()

# --- Loop Principal do Jogo ---

if __name__ == "__main__":
    PLAYER = Jogador(vida=100, energia=100, fome=100)
    JOGO = Partida(PLAYER)
    PLAYER.jogo = JOGO

    while True:
        PLAYER.verificar_status()
        JOGO.hud()
        print("\n" + "."*20 + "\n")
        time.sleep(1)