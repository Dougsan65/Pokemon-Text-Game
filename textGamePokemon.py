import time
import dbconnect
import requests
import datetime
import threading
import random
import pygame
import os


dataAtual = datetime.datetime.now()
try:
    conn = dbconnect.connectdb("PokemonMainDatabase")
    cur = conn.cursor()
except Exception as e:
    print('Erro ao conectar ao banco de dados, verifque os dados novamente!', e)
    raise SystemExit



#Variaveis Globais

PlayerName = ''
infoData = []
pokemonsAtuais = []
dinheiroJogador = 0
jogadorId = 0
InitialPoke = ''
InitialPoke_boolean = False
autoSaveon  = False
perguntaAutoSave = True

itensPrice = {
    'pokebola': 200,
    'superbola': 500,
    'ultrabola': 1000,
    'masterbola': 2000
}

itensJogador = {
    'pokebola': 0,
    'superbola': 0,
    'ultrabola': 0,
    'masterbola': 0
}

pokebolas = {
    'pokebola': 0,
    'superbola': 0,
    'ultrabola': 0,
    'masterbola': 0
}

#Check Functions

def checkPlayesHasPokeballs(idPlayer):
    cur.execute('SELECT * FROM pokebolas WHERE jogador_id = %s', (idPlayer,))#2345
    pokebolasbd = cur.fetchone()
    if not pokebolasbd:
        return False
    else:
        return True

def checkInitialPoke(namePlayer):
    try:
        cur.execute('SELECT pokemon_inicial FROM pokemons WHERE nome_jogador = %s', (namePlayer,))
        checkifExist = cur.fetchall()
    except Exception as e:
        logger(e)
        print('Erro ao verificar se o jogador já escolheu um pokemon inicial', e)
        menu()
    if checkifExist:
        return True
    else:
        return False

def checkAllPlayers():
    cur.execute('SELECT nome FROM players')
    for i in cur.fetchall():
        print(f'Jogador: {i[0]}')
    input('Pressione enter para continuar...')
    logger('Checking Players in Database')
    print('\n')

def checkInfoPlayerLocal():
    print('\n\n')
    print(f'Nome do jogador atual é: {PlayerName}')
    print(f'Jogador ID: {jogadorId[0]}')
    print(f'Dinheiro do jogador: {dinheiroJogador}')
    print(f'Pokemon inicial: {InitialPoke}')
    print(f'Geração escolhida: {geracaoEscolhida}')
    print(checkAllPokemons())
    print(f'Pokebolas atuais:\n Pokebolas: {pokebolas["pokebola"]}\n Superbolas: {pokebolas["superbola"]}\n Ultrabolas: {pokebolas["ultrabola"]}\n Masterbolas: {pokebolas["masterbola"]}\n')
    input('Pressione enter para continuar...')
    logger('Checking Player Info')

def checkAllPokemons():
    try:
        cur.execute('SELECT nome_pokemon FROM pokemons_capturados WHERE jogador_id = %s', (jogadorId,))
        checkPockemon = cur.fetchall()
        pokemonNames = [i[0] for i in checkPockemon]
        return print(f'Pokemons capturados: {", ".join(pokemonNames)}')
    except Exception as e:
        print('Erro ao verificar os pokemons', e)
        logger(f'Error checkAllPokemons:{e}')
        menu()
        
def checkPlayerExists(playerName):
    checkPlayer = cur.execute('SELECT * FROM players WHERE nome = %s', (playerName,))
    checkPlayer = cur.fetchall()
    logger('checkPlayerExists')
    if not checkPlayer:
        return False
    else:
        print(f'Jogador encontrado: {checkPlayer[0][1]} ID: {checkPlayer[0][0]}')
        playerName = checkPlayer[0][1]
        return True

#Funcoes de Data Management

def changePlayer():
    global infoData, PlayerName, InitialPoke, InitialPoke_boolean, pokemonsAtuais, pokebolas
    infoData.clear()
    PlayerName = ''
    InitialPoke = ''
    InitialPoke_boolean = False
    pokemonsAtuais.clear()
    pokebolas = {
        'pokebola': 0,
        'superbola': 0,
        'ultrabola': 0,
        'masterbola': 0
    }
    os.system('cls')
    infoData = input('Digite o nome do jogador: ')
    infoData = [infoData]
    PlayerName = infoData[0]
    if checkPlayerExists(infoData[0]):
        if checkInitialPoke(infoData[0]):
            print('Jogador encontrado, trocando dados...')
            logger('Changing Player: Found Player')
            carregarDados()
        else:
            print('Jogador encontrado, mas não escolheu um pokemon inicial')
            logger('Changing Player: Found Player, No Initial Pokemon')
            escolherGeracaoInicial()
    else:
        newGame()

def salvarDados():
    #Salvar o id, nome, pokemon inicial, geracao, data, pokemons atuais
    global infoData, pokemonsAtuais, InitialPoke, geracaoEscolhida
    if checkPlayerExists(infoData[0]):
        if checkInitialPoke(infoData[0]):
            #Salvar as pokebolas na tebela pokebolas
            #Checar se o id do jogador já existe na tabela pokebolas
            cur.execute('SELECT jogador_id FROM pokebolas WHERE jogador_id = %s', (jogadorId,))
            checkPokebolas = cur.fetchall()
            if not checkPokebolas:
                cur.execute(f"""
    INSERT INTO pokebolas (jogador_id, qntd_pokebola, qntd_superbola, qntd_ultrabola, qntd_masterbola, data_time)
    SELECT id, {3}, {pokebolas['superbola']}, {pokebolas['ultrabola']}, {pokebolas['masterbola']}, '{dataAtual}'
    FROM players
    WHERE nome = '{infoData[0]}';
""")

                conn.commit()
            else:
                cur.execute(f"""
    UPDATE pokebolas
    SET qntd_pokebola = {pokebolas['pokebola']},
        qntd_superbola = {pokebolas['superbola']},
        qntd_ultrabola = {pokebolas['ultrabola']},
        qntd_masterbola = {pokebolas['masterbola']},
        data_time = '{dataAtual}'
    WHERE   jogador_id = {jogadorId[0]};
""")
                conn.commit()
            
            
            #Salvar o dinheiro atual do jogador na tabela players
            cur.execute('UPDATE players SET dinheiro = %s WHERE id = %s', (dinheiroJogador, jogadorId))
            
            logger('Saving Data to Database, Player Exists')
        else:
            logger('Saving Data to Database, New Player')
            cur.execute(f"""
    INSERT INTO pokemons (jogador_id, nome_jogador, pokemon_inicial, geracao, datacriacao)
    SELECT id, nome, '{InitialPoke}', {geracaoEscolhida}, '{dataAtual}'
    FROM players
    WHERE nome = '{infoData[0]}';
""")
            conn.commit()

def autoSave():
    salvarDados()
    logger('autosave')
    threading.Timer(30, autoSave).start()

def carregarDados():
    global infoData, pokemonsAtuais, PokemonInitialCheck, InitialPoke_boolean, pokeInicialEscolhido, InitialPoke, geracaoEscolhida, jogadorId, pokebolas, dinheiroJogador
    if checkInitialPoke(infoData[0]):
        try:
            #Carrega id do jogador
            jogadorId = cur.execute('SELECT id FROM players WHERE nome = %s', (infoData[0],))
            jogadorId = cur.fetchone()
            
            #Carrega os pokemons atuais da tabela pokemons capturados
            cur.execute('SELECT nome_pokemon FROM pokemons_capturados WHERE jogador_id = %s', (jogadorId))
            pokemonsAtuais = cur.fetchall()
            pokemonsAtuais = [i[0] for i in pokemonsAtuais]
            
            #Carrega a geração escolhida
            cur.execute('SELECT geracao FROM pokemons WHERE jogador_id = %s', (jogadorId,))
            geracaoEscolhida = cur.fetchone()
            geracaoEscolhida = geracaoEscolhida[0]
            
            #Carrega o Dinheiro do Jogador
            cur.execute('SELECT dinheiro FROM players WHERE id = %s', (jogadorId,))
            dinheiroJogador = cur.fetchone()
            dinheiroJogador = dinheiroJogador[0]
            
            #Carrega o Poke Inicial
            cur.execute('SELECT pokemon_inicial FROM pokemons WHERE jogador_id = %s', (jogadorId,))
            InitialPoke = cur.fetchone()[0]
            logger('load success')
            
            #Carrega as Pokebolas
            #func to check if the player has a line in the pokebolas table
            if checkPlayesHasPokeballs(jogadorId):
                
                cur.execute('SELECT * FROM pokebolas WHERE jogador_id = %s', (jogadorId,))#2345
                pokebolasbd = cur.fetchone()
                pokebolas = {
                    'pokebola': pokebolasbd[2],
                    'superbola': pokebolasbd[3],
                    'ultrabola': pokebolasbd[4],
                    'masterbola': pokebolasbd[5]
                }
                conn.commit()
                logger('load pokeballs success')
            else:
                logger('player dont have pokeballs')
        except Exception as e:
            print('Erro ao carregar os dados: ', e)
            logger(e)
            menu()
        
#Criar novo personagem

def newGame():
    logger('Creating New character')
    newSave = input('Esse personagem não existe, criando um novo save (s para continuar)')
    if newSave == 's':
        criarSave()
        carregarDados()
        menu()
    else:
        newGame()

def criarSave():
    logger('Creating New character')
    global infoData, PlayerName, InitialPoke_boolean, InitialPoke, jogadorId
    infosNewPlayer = []
    nome = infoData[0]
    PlayerName = infoData[0]
    infosNewPlayer.append(nome)
    idade = input('Digite a idade do jogador: ')
    infosNewPlayer.append(idade)
    cidade = input('Digite a cidade do jogador: ')
    infosNewPlayer.append(cidade)
    expPoke = input('Você já jogou Pokemon?: (s/n)')
    if expPoke == 's':
        expPoke = True
    else:
        expPoke = False
    cur.execute("INSERT INTO players (nome, idade, cidade, datacriacao, exppoke) VALUES (%s, %s, %s, %s, %s);", (infosNewPlayer[0], infosNewPlayer[1], infosNewPlayer[2], dataAtual, expPoke))
    # cur.execute('INSERT INTO jogadores (nome, idade, cidade, expPoke, dataCriacao) VALUES (%s, %s, %s, %s, %s)', (infosNewPlayer[0], infosNewPlayer[1], infosNewPlayer[2], expPoke, dataAtual))
    conn.commit()
    logger('criando save')
    print('Informações adicionadas com sucesso ao db!')
    print('Direcionando para seleção de pokemon inicial...')
    jogadorId = cur.execute('SELECT id FROM players WHERE nome = %s', (infoData[0],))
    jogadorId = cur.fetchone()
    escolherGeracaoInicial()
    return       

def escolherInicial(geracaoEscolhida):
    global InitialPoke, InitialPoke_boolean
    pokemonInicial = input('Escolha seu pokemon inicial: ')
    pokemons = requests.get(f'https://pokeapi.co/api/v2/generation/{geracaoEscolhida}').json().get('pokemon_species')
    for index, pokemon in enumerate(pokemons):
        if index < 3:
            if pokemon['name'] == pokemonInicial:
                print(pokemonInicial, pokemon['name'])
                pokemonsAtuais.append(pokemonInicial)
                print(f'Pokemon inicial escolhido: {pokemonInicial}')
                InitialPoke_boolean = True
                InitialPoke = pokemonInicial
                #pegar o id do pokemonInicial
                try:
                    pokemonSorteadoInit = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{InitialPoke}/').json()
                    
                    pokemonSorteadoID = pokemonSorteadoInit['id']
                except Exception as e:
                    print('Erro ao pegar o id do pokemon', e)
                    logger(e)
                    menu()
                cur.execute('INSERT INTO pokemons_capturados (jogador_id, pokemon_id, nome_pokemon, data_captura) VALUES (%s, %s, %s, %s)', (jogadorId, pokemonSorteadoID, InitialPoke, dataAtual))
                conn.commit()
                logger('First Pokemon Choose')
                salvarDados()
                return
            if index >3:
                print('Pokemon não encontrado, tente novamente')
                escolherInicial(geracaoEscolhida)
        
def escolherGeracaoInicial():
    global geracaoEscolhida
    logger('Chossing First Generation')
    geracaoEscolhida = input('Digite a geração do pokemon: (vazio para ver todas)')
    geracoes = requests.get('https://pokeapi.co/api/v2/generation/').json().get('results')
    if geracaoEscolhida == '':
        for geracao in geracoes:
            print(geracao['name'])
    if geracaoEscolhida in '123456789':
        print(f'Esses são os pokemons iniciais da {geracaoEscolhida} geração:')
        pokemons = requests.get(f'https://pokeapi.co/api/v2/generation/{geracaoEscolhida}').json().get('pokemon_species')
        for index, pokemons in enumerate(pokemons):
            if index < 3:
                print(pokemons['name'])
        choice = input('Deseja escolher essa geracao? (s/n)')
        if choice == 's':
            escolherInicial(geracaoEscolhida)
            pass
        else:
            escolherGeracaoInicial()
    else:
        print('Geração inválida')
        escolherGeracaoInicial()

#Logger
            
def logger(where):
    global infoData
    cur.execute(f"""
    INSERT INTO logsjoin (player_id, nome, locale, date)
    SELECT id, nome, '{where}', '{dataAtual}'
    FROM players
    WHERE nome = '{infoData[0]}';
""")
    if where != 'checkPlayerExists' and where != 'autosave' and where != 'checkInitialPoke':
        conn.commit()
        print(f'Informações de log {where} foram adicionadas com sucesso ao db!\n')
        time.sleep(0.9)
        os.system('cls')
    else:
        conn.commit()


#Audio Func

def playAudioBackground():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load('audios/teste.mp3')
        pygame.mixer.music.set_volume(0.040)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print('Erro ao tocar o audio', e)
        logger(e)
        menu()

#Funcoes para a gameplay

def pegarPokemon():
    global pokemonsAtuais, dinheiroJogador, pokebolas
    os.system('cls')
    try:
        pokemons = requests.get('https://pokeapi.co/api/v2/pokedex/1').json().get('pokemon_entries')
    except Exception as e:
        print('Erro ao pegar os pokemons', e)
        logger(e)
        menu()

    geracoes = {
        1: slice(0, 151),
        2: slice(151, 251),
        3: slice(251, 386),
        4: slice(386, 493),
        5: slice(493, 649),
        6: slice(649, 721),
        7: slice(721, 809),
        8: slice(809, 898),
        9: slice(898, 1000)
    }

    moneyEarned = {
        1: 100,
        2: 200,
        3: 300,
        4: 400,
        5: 500,
        6: 600,
        7: 700,
        8: 800,
        9: 900,
        10: 1000}
    
    if geracaoEscolhida in geracoes:
        try:
            pokemonSorteado = random.choice(pokemons[geracoes[geracaoEscolhida]])
            moneyEarned = random.choice(moneyEarned)
            
        except Exception as e:
            salvarDados()
            print('Erro ao sortear o pokemon', e)
            logger(e)
            menu()
    else:
        print('Geração inválida')
        time.sleep(3)
    
    capturar = input(f'Deseja capturar o pokemon {pokemonSorteado["pokemon_species"]["name"]}? (s/n)')

    if capturar == 's':
        pokemonsAtuais.append(pokemonSorteado['pokemon_species']['name'])

        print(f'Pokemon {pokemonSorteado["pokemon_species"]["name"]} capturado com sucesso!')
        for i in pokebolas:
            print(f'{i}: {pokebolas[i]}')
        choosePokeball = input('Escolha a pokebola que deseja usar: (enter para sair)')
        
        os.system('cls')
        if choosePokeball in pokebolas:
            print(f'Você escolheu a pokebola: {choosePokeball.capitalize()}')
            print('Capturando pokemon...')
            time.sleep(2)
            
            if pokebolas[choosePokeball] == 0:
                print('Você não tem pokebolas suficientes')
                time.sleep(2)
                return menu()
        elif choosePokeball == '':
            return menu()           
        else:
            print('Escolha inválida')
            logger('Invalid Choice to choose pokeball')
            return pegarPokemon()
        

        try:
            dinheiroJogador += moneyEarned
            pokebolas[choosePokeball] -= 1
            cur.execute('INSERT INTO pokemons_capturados (jogador_id, pokemon_id, nome_pokemon, data_captura) VALUES (%s, %s, %s, %s)', (jogadorId, pokemonSorteado['entry_number'], pokemonSorteado['pokemon_species']['name'], dataAtual))
            conn.commit()
            cur.execute('UPDATE players SET dinheiro = %s WHERE id = %s', (dinheiroJogador, jogadorId))
            
            logger('Capturando Pokemon')
            conn.commit()
        except Exception as e:
            print('Erro ao capturar o pokemon', e)
            logger(e)
            return menu()

        print(f'Pokemon {pokemonSorteado["pokemon_species"]["name"]} capturado com sucesso!')
        print(f'Você ganhou {moneyEarned} de dinheiro')
        
        time.sleep(5)
        return menu()
    else:
        option = input('Deseja tentar novamente? (s/n)')
        if option == 's':
            return pegarPokemon()
        else:
            print('Pokemon não capturado')
            logger('Pokemon not captured')
            return menu()
    
    
   

def gerenciamentoPokebolas():
    global pokebolas, dinheiroJogador
    logger('Getting Pokeballs')
    print(f'Pokebolas: {pokebolas["pokebola"]} Superbolas: {pokebolas["superbola"]} Ultrabolas: {pokebolas["ultrabola"]} Masterbolas: {pokebolas["masterbola"]}')
    print(f'Dinheiro atual: {dinheiroJogador}')
    print('Preço das pokebolas:\n'
          '(1) - Pokebola: 200\n'
          '(2) - Superbola: 500\n'
          '(3) - Ultrabola: 1000\n'
          '(4) - Masterbola: 2000\n')
    escolha = input('Escolha a pokebola que deseja comprar: (enter para sair)')
    if escolha not in '1234':
        print('Escolha inválida')
        gerenciamentoPokebolas()
    if escolha == '':
        return menu()
    

    quantidade = int(input('Digite a quantidade: '))
    if escolha in '1234':
        if dinheiroJogador < (itensPrice[list(itensPrice.keys())[int(escolha)-1]] * quantidade):
            print('Você não tem dinheiro suficiente')
            time.sleep(3)
            return menu()
        else:
            dinheiroJogador -= (itensPrice[list(itensPrice.keys())[int(escolha)-1]] * quantidade)
            pokebolas[list(pokebolas.keys())[int(escolha)-1]] += quantidade
            print('Compra realizada com sucesso!')
            logger('Buying Pokeballs')
            time.sleep(3)
            return menu()

def lojaItens():
    pass

#Menu Principal 
        
def menu():
    global pokemonsAtuais, infoData, pokeInicialEscolhido, dado, InitialPoke_boolean, InitialPoke, PlayerName, autoSaveon, perguntaAutoSave
    salvarDados()
    print(f'Bem-vindo {infoData[0]} ao menu do jogo!')
    print('Escolha a opção:\n'
      '  (1) - New Game (nothing yet)\n'
      '  (2) - Null\n'
      '  (3) - Ver Pokedex\n'
      '  (4) - --Insert--\n'
      '  (5) - Salvar\n'
      '  (6) - Ver Informações do Jogador\n'
      '  (7) - Ver Jogadores Salvos no Banco de Dados\n'
      '  (8) - Escolher outro Personagem\n'
      '  (9) - Escolher Pokemon Inicial\n'
      ' (10) - Pegar Pokemon\n'
      ' (11) - Gerenciamento de Pokebolas\n'
      ' (12) - Sair\n')
    
    escolha = input('Escolha a opção: ')
    
    if escolha == '1': #New Game
        logger('Entering New Game')
 
    elif escolha == '2':
        pass
        
    elif escolha == '3':
        logger('Checking Pokedex')
        pokedex = requests.get('https://pokeapi.co/api/v2/pokedex/1').json().get('pokemon_entries')
        verPokedex = input(f'Digite 1 para ver o numero de pokemons capturados, 2 para ver a pokedex: ')
        if verPokedex == '1':
            print(f'{len(pokemonsAtuais)}/{len(pokedex)} pokemons capturados')
            input('Pressione enter para continuar...')
        elif verPokedex == '2':
            for pokemon in pokedex:
                print(pokemon['pokemon_species']['name'])
            input('Pressione enter para continuar...')
        
    elif escolha == '4':
        pass

    elif escolha == '5':
        if perguntaAutoSave:
            print('Apenas ligue se já tiver salvo os dados pelo menos uma vez!')
            a = input('Deseja ligar o auto save? (s/n)')
        
        if perguntaAutoSave and a == 's':
            autoSaveon = True
            perguntaAutoSave = False
            autoSave()
        salvarDados() 
        print('Informações adicionadas com sucesso ao db!')
        menu()
    
    elif escolha == '6':
        checkInfoPlayerLocal()
        
    
    elif escolha == '7':
        checkAllPlayers()
        
    elif escolha == '8':
        changePlayer()
    
    elif escolha == '9':
        logger('Choosing First Pokemon')
        cur.execute('SELECT pokemon_inicial FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
        checkifExist = cur.fetchall()
        if checkifExist:
            print('Você já escolheu um pokemon inicial')
            menu()
        else:
            escolherGeracaoInicial()
    
    elif escolha == '10':
        pegarPokemon()
        
    elif escolha == '11':
        gerenciamentoPokebolas()
        
    elif escolha == '12':
        logger('Exiting Game')
        dbconnect.disconnectdb(conn)
        raise SystemExit

os.system('cls')
infoData = input('Digite o nome do jogador: ').lower()
infoData = [infoData]
PlayerName = infoData[0]

if checkPlayerExists(infoData[0]):
    carregarDados()
    
else:
    newGame()
    
audio_thread = threading.Thread(target=playAudioBackground)
audio_thread.daemon = True
audio_thread.start()

while True:
    menu()