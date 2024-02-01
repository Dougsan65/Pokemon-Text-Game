import requests
import dbconnect
import datetime
from difflib import get_close_matches
import threading
import time

dataAtual = datetime.datetime.now()
conn = dbconnect.connectdb()
cursor = conn.cursor()



pokemons = []
pokemonsUnicos = set()
Pontos1 = 0
Pontos2 = 0
rounds = 0
winner = ''

urlPokemons = 'https://pokeapi.co/api/v2/pokemon?limit=5000'
pokemonsResponse = requests.get(urlPokemons)
if pokemonsResponse.status_code == 200:
    print('Conexão com a API bem-sucedida')
    results = pokemonsResponse.json().get('results')
    for pokemon in results:
        pokemons.append(pokemon['name'])
else:
    print('Deu merda ai')
        
nomeJogador1 = input('Digite o nome do jogador 1: ')
nomeJogador2 = input('Digite o nome do jogador 2: ')
numJogadas = int(input('Digite o numero de pokemons que serão encontrados: (0 para default)'))
if numJogadas == 0:
    numJogadas = 10
timerTemp = int(input('Digite o tempo de cada jogada: (0 para default)'))
if timerTemp == 0:
    timerTemp = 15

def temporizador():
    global timer
    timer = timerTemp
    while timer > 0:
        time.sleep(1)
        timer -= 1
    
def temporizador2():
    global timer
    timer = timerTemp
    while timer > 0:
        time.sleep(1)
        timer -= 1

def Jogador1():
    global Pontos1, timer, nomeJogador1, rounds
    rounds += 1

    threading.Thread(target=temporizador).start()
    print('\n\n')
    print(f'Temporarizador de {timerTemp} segundos iniciado.')
    print(f'Vez do {nomeJogador1}. Digite o nome de um Pokémon valido, você atualmente tem {Pontos1} pontos')
    print(f'Quantidade de Pokemons encontrados: {len(pokemonsUnicos)}, faltam {numJogadas - len(pokemonsUnicos)} para acabar a partida.')
    nomePoke = input('Digite o nome do Pokémon: ').lower()

    
    if timer == 0:
        print('Tempo expirado, sem entrada do usuário.')
        return
    
    if nomePoke in pokemonsUnicos:
        print('O Pokémon já foi encontrado.')
        return 
    if nomePoke in pokemons:
        print('Pokemon encontrado')
        Pontos1 += 1
        print(f'Jogador 1: {Pontos1} pontos')
        pokemonsUnicos.add(nomePoke)
        return
    else:
        print('Pokemon não encontrado')
        palavra_proxima = get_close_matches(nomePoke, pokemons, n=1, cutoff=0.8)
        if palavra_proxima == []:
            print('Você perdeu a vez, o pokemon não existe')
            return
        valorFormatado = ''.join(map(str, palavra_proxima))
        palavraProxima = input(f'Você quis dizer {valorFormatado.capitalize()}? (s/n): ')
        nomePoke = valorFormatado
        if palavraProxima == 's':
            if nomePoke in pokemonsUnicos:
                print('O Pokémon já foi encontrado.')
                return
            print('Pokemon encontrado')
            Pontos1 += 1
            print(f'Jogador 1: {Pontos1} pontos')
            pokemonsUnicos.add(nomePoke)
            print(pokemonsUnicos)
            return
        else:
            print('Você perdeu a vez')
            return
        
def Jogador2():
    global Pontos2, timer, nomeJogador2, rounds
    rounds += 1
    temporizador_thread = threading.Thread(target=temporizador2)
    temporizador_thread.start()
    print('\n\n')
    print(f'Temporarizador de {timerTemp} segundos iniciado.')
    print(f'Vez do {nomeJogador2}. Digite o nome de um Pokémon valido, você atualmente tem {Pontos2} pontos')
    print(f'Quantidade de Pokemons encontrados: {len(pokemonsUnicos)}, faltam {numJogadas - len(pokemonsUnicos)} para acabar a partida.')
    nomePoke = input('Digite o nome do Pokémon: ').lower()
    
    if timer == 0:
        print('Tempo expirado, sem entrada do usuário.')
        return
    
    
    if nomePoke in pokemonsUnicos:
        print('O Pokémon já foi encontrado.')
        return 
    if nomePoke in pokemons:
        print('Pokemon encontrado')
        Pontos2 += 1
        print(f'Jogador 2: {Pontos2} pontos')
        pokemonsUnicos.add(nomePoke)
        return 
    else:
        print('Pokemon não encontrado')
        palavra_proxima = get_close_matches(nomePoke, pokemons, n=1, cutoff=0.8)
        if palavra_proxima == []:
            print('Você perdeu a vez, o pokemon não existe')
            return
        valorFormatado = ''.join(map(str, palavra_proxima))
        palavraProxima = input(f'Você quis dizer {valorFormatado.capitalize()}? (s/n): ')
        nomePoke = valorFormatado
        if palavraProxima == 's':
            if nomePoke in pokemonsUnicos:
                print('O Pokémon já foi encontrado.')
                return
            print('Pokemon encontrado')
            Pontos2 += 1
            print(f'Jogador 1: {Pontos1} pontos')
            pokemonsUnicos.add(nomePoke)
            print(pokemonsUnicos)
            return
        else:
            print('Você perdeu a vez')
            return

while True:
    print('\n\n')
    print(f'Jogador 1: {Pontos1} pontos')
    print(f'Jogador 2: {Pontos2} pontos')
    Jogador1()
    Jogador2()
    
    if len(pokemonsUnicos) == numJogadas:
        print('Todos os pokemons foram encontrados.')
        if Pontos1 > Pontos2:
            print('Jogador 1 venceu')
            winner = nomeJogador1
            
            break
        elif Pontos1 < Pontos2:
            print('Jogador 2 venceu')
            winner = nomeJogador2
            break
        else:
            print('Empate')
            winner = 'Empate'
            break
listaPokemons = list(pokemonsUnicos)
cursor.execute('INSERT INTO pokemons (nomejogador1, nomejogador2, rounds, vencedor, data, qntdpokes, pontosjogador2, pontosjogador1, pokemonsusados) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (nomeJogador1, nomeJogador2, rounds, winner, dataAtual, numJogadas, Pontos2, Pontos1, listaPokemons))
conn.commit()
dbconnect.disconnectdb(conn)
