import dbconnect
import requests
import datetime
import threading
import random
import pygame


dataAtual = datetime.datetime.now()
try:
    conn = dbconnect.connectdb("PokemonMainDatabase")
    cur = conn.cursor()
except Exception as e:
    print('Erro ao conectar ao banco de dados, verifque os dados novamente!', e)
    raise SystemExit




pokemonsAtuais = []
jogadorId = 0
infoData = [] #[0] Player Name
InitialPoke_boolean = False
PlayerName = ''
InitialPoke = ''
autoSaveon  = False
perguntaAutoSave = True

#Check Functions

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
    logger('Checking Players in Database')
    cur.execute('SELECT nome FROM players')
    for i in cur.fetchall():
        print(f'Jogador: {i[0]}')

def checkAllPokemons():
    logger('Checking Pokemons in Database')
    print(jogadorId)
    #Selecionar ID do jgoador e pesquisar os pokemons na tabela pkoemons_capturados
    cur.execute('SELECT nome_pokemon FROM pokemons_capturados WHERE jogador_id = %s', (jogadorId,))
    checkPockemon = cur.fetchall()
    for i in checkPockemon:
        print(f'Pokemons: {i[0]}')
        
def checkPlayerExists(playerName):
    checkPlayer = cur.execute('SELECT * FROM players WHERE nome = %s', (playerName,))
    checkPlayer = cur.fetchall()
    logger('checkPlayerExists')
    if not checkPlayer:
        return False
    else:
        print(f'Jogador encontrado: {checkPlayer[0][1]}\n')
        playerName = checkPlayer[0][1]
        return True

#Funcoes de Data Management

def changePlayer():
    global infoData, PlayerName, InitialPoke, InitialPoke_boolean, pokemonsAtuais
    infoData.clear()
    PlayerName = ''
    InitialPoke = ''
    InitialPoke_boolean = False
    pokemonsAtuais.clear()
    print(pokemonsAtuais)
    infoData = input('Digite o nome do jogador: ')
    infoData = [infoData]
    PlayerName = infoData[0]
    if checkPlayerExists(infoData[0]):
        if checkInitialPoke(infoData[0]):
            print('Jogador encontrado, trocando dados...')
            carregarDados()
        else:
            print('Jogador encontrado, mas não escolheu um pokemon inicial')
            escolherGeracaoInicial()
    else:
        newGame()

def salvarDados():
    #Salvar o id, nome, pokemon inicial, geracao, data, pokemons atuais
    global infoData, pokemonsAtuais, InitialPoke, geracaoEscolhida
    if checkPlayerExists(infoData[0]):
        if checkInitialPoke(infoData[0]):
            #Salvar os pokemons da tabela pokemon capturados na lista de pokemons atuais
            cur.execute('SELECT nome_pokemon FROM pokemons_capturados WHERE jogador_id = %s', (jogadorId,))
            pokemonsAtuais = cur.fetchall()
            pokemonsAtuais = [i[0] for i in pokemonsAtuais]
            print(pokemonsAtuais)
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
    global autoSaveon
    global infoData, pokemonsAtuais, InitialPoke, geracaoEscolhida
    if checkPlayerExists(infoData[0]):
        if checkInitialPoke(infoData[0]):
            #Salvar os pokemons da tabela pokemon capturados na lista de pokemons atuais
            cur.execute('SELECT nome_pokemon FROM pokemons_capturados WHERE jogador_id = %s', (jogadorId,))
            pokemonsAtuais = cur.fetchall()
            pokemonsAtuais = [i[0] for i in pokemonsAtuais]
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
    logger('autosave')
    threading.Timer(30, autoSave).start()

def carregarDados():
    global infoData, pokemonsAtuais, PokemonInitialCheck, InitialPoke_boolean, pokeInicialEscolhido, InitialPoke, geracaoEscolhida, jogadorId
    if checkInitialPoke(infoData[0]):
        try:
            jogadorId = cur.execute('SELECT id FROM players WHERE nome = %s', (infoData[0],))
            jogadorId = cur.fetchone()
            print(jogadorId)
            
            #Carrega os pokemons atuais da tabela pokemons capturados
            cur.execute('SELECT nome_pokemon FROM pokemons_capturados WHERE jogador_id = %s', (jogadorId,))
            pokemonsAtuais = cur.fetchall()
            pokemonsAtuais = [i[0] for i in pokemonsAtuais]
            
            #Carrega a geração escolhida
            cur.execute('SELECT geracao FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
            geracaoEscolhida = cur.fetchone()
            geracaoEscolhida = geracaoEscolhida[0]
            logger('load data')
        except Exception as e:
            print('Erro ao carregar os dados', e)
            logger(e)
            menu()
        
#Criar novo personagem

def newGame():
    logger('Creating New character')
    newSave = input('Esse personagem não existe, criando um novo save (s para continuar)')
    if newSave == 's':
        criarSave()
        menu()
    else:
        raise SystemExit

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
    jogadorId = cur.fetchone()[0]
    escolherGeracaoInicial()
    return       

def escolherInicial(geracaoEscolhida): #FUNCIONA
    global InitialPoke, InitialPoke_boolean
    pokemonInicial = input('Escolha seu pokemon inicial: ')
    pokemons = requests.get(f'https://pokeapi.co/api/v2/generation/{geracaoEscolhida}').json().get('pokemon_species')
    for index, pokemon in enumerate(pokemons):
        if index < 3:
            print(pokemon['name'])
            
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

#Logger
            
def logger(where):
    global infoData
    cur.execute(f"""
    INSERT INTO logsjoin (player_id, nome, locale, date)
    SELECT id, nome, '{where}','{dataAtual}'
    FROM players
    WHERE nome = '{infoData[0]}';
""")
    conn.commit()
    print(f'Informações de log {where} foram adicionadas com sucesso ao db!\n')

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
    print(geracaoEscolhida)
    if geracaoEscolhida in geracoes:
        pokemonSorteado = random.choice(pokemons[geracoes[geracaoEscolhida]])
    
    capturar = input(f'Deseja capturar o pokemon {pokemonSorteado["pokemon_species"]["name"]}? (s/n)')    
    if capturar == 's':
        pokemonsAtuais.append(pokemonSorteado['pokemon_species']['name'])
        print(f'Pokemon {pokemonSorteado["pokemon_species"]["name"]} capturado com sucesso!')
        try:
            cur.execute('INSERT INTO pokemons_capturados (jogador_id, pokemon_id, nome_pokemon, data_captura) VALUES (%s, %s, %s, %s)', (jogadorId, pokemonSorteado['entry_number'], pokemonSorteado['pokemon_species']['name'], dataAtual))
            logger('Capturando Pokemon')
            conn.commit()
        except Exception as e:
            print('Erro ao capturar o pokemon', e)
            logger(e)
            menu()
        print(f'Pokemons atuais: {pokemonsAtuais}')
        menu()
    else:
        print('Pokemon não capturado')
        menu()
        
#Menu Principal 
        
def menu():
    global pokemonsAtuais, infoData, pokeInicialEscolhido, dado, InitialPoke_boolean, InitialPoke, PlayerName, autoSaveon, perguntaAutoSave


    print(f'Pokemons atuais: {pokemonsAtuais}')
    print('Bem-vindo ao menu do jogo!')
    print('Escolha a opção: \n(1) - New Game \n(2) - Ver Pokemons Salvos no Banco de Dados\n(3) - Ver Pokedex \n(4) - Sair \n(5) - Salvar \n(6) - Ver Informações do Jogador \n(7) - Ver Jogadores Salvos no Banco de Dados\n(8) - Escolher outro Personagem\n(9) - Escolher Pokemon Inicial\n')
    
    
    escolha = input('Escolha a opção: ')
    
    
    if escolha == '1':
        logger('Entering New Game')
 
    elif escolha == '2':
        logger('Checking Database for Pokemons')
        checkAllPokemons()
        menu()
        
    elif escolha == '3':
        logger('Checking Pokedex')
        pokedex = requests.get('https://pokeapi.co/api/v2/pokedex/1').json().get('pokemon_entries')
        verPokedex = input(f'Digite 1 para ver o numero de pokemons capturados, 2 para ver a pokedex: ')
        if verPokedex == '1':
            print(f'{len(pokemonsAtuais)}/{len(pokedex)} pokemons capturados')
        elif verPokedex == '2':
            for pokemon in pokedex:
                print(pokemon['pokemon_species']['name'])
        
    elif escolha == '4':
        logger('Exiting Game')
        dbconnect.disconnectdb(conn)
        raise SystemExit

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
        logger('Checking Info Player Local')
        print(f'Nome do jogador atual é: {PlayerName}')
        print(f'Jogador ID: {jogadorId}')
        print(f'Seus pokemons atuais são: {pokemonsAtuais}')
    
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

infoData = input('Digite o nome do jogador: ').lower()
infoData = [infoData]
PlayerName = infoData[0]

if checkPlayerExists(infoData[0]):
    jogadorId = cur.execute('SELECT id FROM players WHERE nome = %s', (infoData[0],))
    jogadorId = cur.fetchone()
    
    print(f'Jogador encontrado: {infoData[0]} {jogadorId[0]}\n')
    print('Jogador encontrado')
    carregarDados()
    
else:
    newGame()
    
audio_thread = threading.Thread(target=playAudioBackground)
audio_thread.daemon = True
audio_thread.start()

while True:
    menu()
    
