import dbconnect
import requests
import datetime
import threading
dataAtual = datetime.datetime.now()
conn = dbconnect.connectdb("PokemonGame")
cur = conn.cursor()



pokemonsAtuais = []
infoData = [] #[0] Player Name
InitialPoke_boolean = False
PlayerName = ''
InitialPoke = ''
autoSaveon  = True



def salvarGame():
    global pokemonsAtuais, infoData, InitialPoke, geracaoEscolhida, autoSaveon
    cur.execute('SELECT nome_jogador FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
    nomePlayerExist = cur.fetchall()
    if nomePlayerExist:
        cur.execute('UPDATE pokemons SET pokemons_atuais = %s WHERE nome_jogador = %s', (pokemonsAtuais[0], infoData[0]))  # Ajuste aqui
    else:
        cur.execute('INSERT INTO pokemons (nome_jogador, nome_inicial, pokemons_atuais, geracao, dataCriacao) VALUES (%s, %s, %s, %s, %s)', (infoData[0], InitialPoke, pokemonsAtuais[0], geracaoEscolhida, dataAtual))  # Ajuste aqui
    conn.commit()
    if autoSaveon:
        print('Auto Save ativado!')
        autoSaveon = False
    logger('autosave')
    threading.Timer(30, salvarGame).start()

def checkPlayerExists(playerName):
    checkPlayer = cur.execute('SELECT * FROM jogadores WHERE nome = %s', (playerName,))
    checkPlayer = cur.fetchall()
    logger('checkPlayerExists')
    if not checkPlayer:
        return False
    else:
        print(f'Jogador encontrado: {checkPlayer[0][1]}\n')
        playerName = checkPlayer[0][1]
        return True

def carregarDados():
    global infoData, pokemonsAtuais, PokemonInitialCheck, InitialPoke_boolean, pokeInicialEscolhido, InitialPoke, geracaoEscolhida
    #Carrega os pokemons atuais
    cur.execute('SELECT pokemons_atuais FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
    pokemonsAtuais = cur.fetchall()
    
    #Carrega a geração escolhida
    geracaoEscolhida = cur.execute('SELECT geracao FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
    geracaoEscolhida = cur.fetchall()
    geracaoEscolhida = int(geracaoEscolhida[0][0])
    
    #Carrega Pokemon inicial
    PokemonInitialCheck = cur.execute('SELECT nome_inicial FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
    PokemonInitialCheck = cur.fetchall()
    if PokemonInitialCheck != None:
        InitialPoke_boolean = True
        InitialPoke = PokemonInitialCheck
    logger('load data')
    print('Carregando save...\n')

def newGame():
    logger('Creating New character')
    newSave = input('Esse personagem não existe, criando um novo save (s para continuar)')
    if newSave == 's':
        criarSave()
        menu()
    else:
        raise SystemExit

def logger(where):
    global infoData
    cur.execute('INSERT INTO logsJoin (nome, dateJoin, locale) VALUES (%s, %s, %s)', (infoData[0], dataAtual, where))
    conn.commit()
    print(f'Informações de log {where} foram adicionadas com sucesso ao db!\n')

def criarSave():
    logger('Creating New character')
    global infoData, PlayerName, InitialPoke_boolean, InitialPoke
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
    cur.execute('INSERT INTO jogadores (nome, idade, cidade, expPoke, dataCriacao) VALUES (%s, %s, %s, %s, %s)', (infosNewPlayer[0], infosNewPlayer[1], infosNewPlayer[2], expPoke, dataAtual))
    conn.commit()
    logger('criando save')
    print('Informações adicionadas com sucesso ao db!')
    print('Direcionando para seleção de pokemon inicial...')
    escolherGeracaoInicial()
    return       

def escolherInicial(geracaoEscolhida):
    global InitialPoke, InitialPoke_boolean
    logger('Chossing First Pokemon')
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
            
def menu():
    global pokemonsAtuais, infoData, pokeInicialEscolhido, dado, InitialPoke_boolean, InitialPoke, PlayerName
    print('Bem-vindo ao menu do jogo!')
    print(InitialPoke)
    print('Escolha a opção: \n(1) - New Game \n(2) - Ver Pokemons Salvos no Banco de Dados\n(3) - Ver Pokedex \n(4) - Sair \n(5) - Salvar \n(6) - Ver Informações do Jogador \n(7) - Ver Jogadores Salvos no Banco de Dados\n(8) - Escolher outro Personagem\n(9) - Escolher Pokemon Inicial\n')
    escolha = input('Escolha a opção: ')
    if escolha == '1':
        logger('Entering New Game')
        pass
    
    elif escolha == '2':
        logger('Checking Database for Pokemons')
        cur.execute('SELECT pokemons_atuais FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
        print(f'Seus pokemons atuais são: {cur.fetchall()}\n')
        menu()
        
    elif escolha == '3':
        logger('Checking Pokedex')
        pokedex = requests.get('https://pokeapi.co/api/v2/pokedex/1').json().get('pokemon_entries')
        verPokedex = input(f'Digite 1 para ver o numero de pokemons capturados, 2 para ver a pokedex: ')
        if verPokedex == '1':
            print(f'{len(pokemonsAtuais)}/{len(pokedex)} pokemons capturados')
        
    elif escolha == '4':
        logger('Exiting Game')
        dbconnect.disconnectdb(conn)
        raise SystemExit

    elif escolha == '5':
        logger('Saving Data to Database')
        cur.execute('SELECT nome_jogador FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
        nomePlayerExist = cur.fetchall()
        if nomePlayerExist:
            cur.execute('UPDATE pokemons SET pokemons_atuais = %s WHERE nome_jogador = %s', (pokemonsAtuais[0], infoData[0]))  # Ajuste aqui
        else:
            cur.execute('INSERT INTO pokemons (nome_jogador, nome_inicial, pokemons_atuais, geracao, dataCriacao) VALUES (%s, %s, %s, %s, %s)', (infoData[0], InitialPoke, pokemonsAtuais[0], geracaoEscolhida, dataAtual))  # Ajuste aqui
        conn.commit()


        


        
        
        print('Informações adicionadas com sucesso ao db!')
        menu()
    
    elif escolha == '6':
        logger('Checking Info Player')
        print(f'Nome do jogador atual é: {PlayerName}')
        print(f'Seus pokemons atuais são: {pokemonsAtuais}')
    
    elif escolha == '7':
        logger('Checking Players in Database')
        cur.execute('SELECT nome FROM jogadores')
        for i in cur.fetchall():
            print(f'Jogador: {i[0]}')
    
    elif escolha == '8':
        logger('Changing Player Character')
        infoData.clear()
        PlayerName = ''
        InitialPoke = ''
        InitialPoke_boolean = False
        pokemonsAtuais.clear()
        infoData = input('Digite o nome do jogador: ')
        infoData = [infoData]
        PlayerName = infoData[0]
        if checkPlayerExists(infoData[0]):
            carregarDados()
        else:
            newGame()
    
    elif escolha == '9':
        logger('Choosing First Pokemon')
        cur.execute('SELECT nome_inicial FROM pokemons WHERE nome_jogador = %s', (infoData[0],))
        checkifExist = cur.fetchall()
        if checkifExist:
            print('Você já escolheu um pokemon inicial')
            menu()
        else:
            escolherGeracaoInicial()

infoData = input('Digite o nome do jogador: ')
infoData = [infoData]
PlayerName = infoData[0]

if checkPlayerExists(infoData[0]):
    carregarDados()
else:
    newGame()
    
    
salvarGame()
while True:
    menu()
