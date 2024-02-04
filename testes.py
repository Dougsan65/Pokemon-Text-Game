import requests
import os



jogador1Pontos = jogador2Pontos = 0


pokemonsEncontrados = set()

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def turnoJogador1():
    global jogador1Pontos
    print('\n\n')
    print(f'Vez do jogador 1. Digite o nome de um Pokémon valido')
    nomePoke = input('Digite o nome do Pokémon: ').lower()
    url = f'https://pokeapi.co/api/v2/pokemon/{nomePoke}/'
    response = requests.get(url)
    if response.status_code == 200:
        if nomePoke in pokemonsEncontrados:
            print('O Pokémon já foi encontrado.') 
            return
        limpar_tela()
        print('Pokemon encontrado')
        jogador1Pontos += 1
        print(f'Jogador 1: {jogador1Pontos} pontos')
        pokemonsEncontrados.add(nomePoke)
    else:
        print('Você perdeu. O Pokémon não existe.')
        jogador1Pontos -= 1

def turnoJogador2():
    global jogador2Pontos
    print('\n\n')
    print(f'Vez do jogador 2. Digite o nome de um Pokémon valido')
    nomePoke = input('Digite o nome do Pokémon: ').lower()
    url = f'https://pokeapi.co/api/v2/pokemon/{nomePoke}/'
    response = requests.get(url)
    if response.status_code == 200:
        if nomePoke in pokemonsEncontrados:
            print('O Pokémon já foi encontrado.')
            return
        print('Pokemon encontrado')
        jogador2Pontos += 1
        print(f'Jogador 2: {jogador2Pontos} pontos')
        pokemonsEncontrados.add(nomePoke)
        return
    else:
        print('Você perdeu. O Pokémon não existe.')
        jogador2Pontos -= 1
        return
        
while True:
    turnoJogador1()
    turnoJogador2()
    if len(pokemonsEncontrados) == 5:
        print('Todos os pokemons foram encontrados.')
        if jogador1Pontos > jogador2Pontos:
            print('Jogador 1 ganhou.')
            break
        else:
            print('Jogador 2 ganhou.')
            break
