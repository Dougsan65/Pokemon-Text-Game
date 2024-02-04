import requests
import os
import json
import dbconnect
from tkinter import filedialog
from tkinter import Tk
root = Tk()
root.withdraw()
root.attributes('-topmost', True)

conn = dbconnect.connectdb()
cursor = conn.cursor()

def arquivo_existe(caminho_completo):
    return os.path.exists(caminho_completo)

def salvar_arquivo(pokemon_data, nome_arquivo):
    with open(nome_arquivo, 'w') as file:
        json.dump(pokemon_data, file, indent=2)

while True:

    nomePokemon = input('Digite o nome do Pokémon: (-sair- para sair) ').lower()
    if nomePokemon == 'sair':
        break
    numeroHabilidade = int(input('Digite o número da habilidade: '))-1
    
    url = f'https://pokeapi.co/api/v2/pokemon/{nomePokemon}/'
    response = requests.get(url)
    
    if response.status_code == 200:
        print('Pokemon encontrado')
        datas = {
            'alldata': response.json(),
            'abilities': response.json().get('abilities', []),
            'forms': response.json().get('forms', []),
            'game_indices': response.json().get('game_indices', []),
            'held_items': response.json().get('held_items', []),
            'id': response.json().get('id', []),
            'is_default': response.json().get('is_default', []),
            'location_area_encounters': response.json().get('location_area_encounters', []),
            'moves': response.json().get('moves', []),
            'name': response.json().get('name', []),
            'order': response.json().get('order', []),
            'species': response.json().get('species', []),
            'sprites': response.json().get('sprites', []),
            'stats': response.json().get('stats', []),
            'types': response.json().get('types', []),
            'weight': response.json().get('weight', [])
        }
        
        salvarPokemon = input(f'Deseja salvar o Pokémon? {datas["name"].upper()}(s/n) ').lower()
        if salvarPokemon == 's':
            typeData = input(f'Deseja salvar que data do {nomePokemon}? alldata \n abilities\n forms\n game_indices\n held_items\n id\n is_default\n location_area_encounters\n moves\n name\n order \n species\n sprites \n stats\n types\n weight ').lower()
            print('Salvando o Pokémon...')
            diretorio_escolhido = filedialog.askdirectory()
            if diretorio_escolhido:
                nome_arquivo = f'{datas["name"]}_{typeData}_data.json'
                caminho_completo = f'{diretorio_escolhido}/{nome_arquivo}'
                
            if arquivo_existe(caminho_completo):
                print(f'Arquivo {nome_arquivo} já existe.')
            else:
                obj = datas.get(typeData)
                if obj != None:
                    print(f'Salvando o  {nome_arquivo} no {caminho_completo}.')
                    salvar_arquivo(obj, caminho_completo)
                else:
                    print('Data não encontrada.')
            if arquivo_existe(caminho_completo):
                print(f'Arquivo {nome_arquivo} salvo com sucesso.')
            
        else:
            print('Nenhum diretório selecionado. Operação cancelada.')



        if not datas['moves']:
            print('O Pokémon não tem habilidades.')
        elif 0 <= numeroHabilidade < len(datas['moves']):
            print(f'O Pokémon tem {len(datas['moves'])} habilidades.')
            print(f'A habilidade {numeroHabilidade + 1} do Pokémon é: {datas['moves'][numeroHabilidade]["move"]["name"]}')
        else:
            print('Número de habilidade inválido para este Pokémon.')
    else:
        print(f'Erro na solicitação. Código de status: {response.status_code}')
