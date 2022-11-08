from definições import frases, estados, partidas
import discord
from discord.ext import commands
from random import choice
from re import fullmatch
from os import getenv
from os.path import exists
from dotenv import load_dotenv
import pymongo

# Carregar variáveis de ambiente
load_dotenv()

# Iniciar base de dados com as definições do jogo
usuario = getenv('MONGODB_USERNAME')
senha = getenv('MONGODB_PASSWORD')
cluster = getenv('MONGODB_CLUSTER')
uri = "".join(["mongodb+srv://", usuario, ":", senha, "@",
              cluster, "/?retryWrites=true&w=majority"])
mongo_client = pymongo.MongoClient(uri)
database = mongo_client.chatbot
#
# Frases
frases_db = database.frases
frases_db.drop()
frases_db.insert_many(frases)
#
# Estados do jogo
estados_db = database.estados
estados_db.drop()
estados_db.insert_many(estados)
#
# Partidas
partidas_db = database.partidas

# Iniciar bot
intents = discord.Intents.default()
intents.message_content = True
prefix = '-'
bot = commands.Bot(intents=intents, command_prefix=prefix)


@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.event
async def on_message(msg):
    #
    # Testar se o autor é um bot (msg.author.bot é verdadeiro)
    # e, se for, simplesmente ignorar a mensagem
    if msg.author.bot:
        return
    autor = msg.author.id
    #
    # Filtrar comando por prefixo
    if msg.content.strip()[0] == prefix:
        mensagem = msg.content.strip()[1:]
    else:
        return
    #
    # Garantir que o autor tem dados de partida
    if autor not in partidas:
        #
        # Jogador começa no estado 0 e inventário vazio
        partidas_db.insert_one({'jogador': autor, 'estado': 0, inventario: {}})
    #
    # Testar se o canal é pvt (msg.channel.type.name == 'private')
    # e, se for, avisar o jogador e continua o jogo sem áudio
    if msg.channel.type.name == 'private':
        # Avisar ao jogador apenas quando o estado for 0
        if (partidas[autor]['estado'] == 0):
            frase = frases_db.find_one({'chave': 'canal_privado'}, {
                                       '_id': 0, 'valor': 1})
            await msg.channel.send(frase['valor'])
            frase = frases_db.find_one({'chave': 'sem_canal_de_voz'}, {
                                       '_id': 0, 'valor': 1})
            await msg.channel.send(frases['valor'])
            partidas[autor]['canal_de_voz'] = None
    #
    # Testar se a mensagem foi mandada em um chat de servidor
    # se sim, testar se o jogador está em canal de voz,
    # caso não esteja convidá-lo a entrar em um.
    if msg.channel.type.name != 'private':
        if msg.author.voice:
            if msg.guild.me not in msg.author.voice.channel.members:
                partidas[autor]['canal_de_voz'] = await msg.author.voice.channel.connect()
            canal_de_voz = partidas[autor]['canal_de_voz']
        else:
            await msg.channel.send(frases['sem_canal_de_voz'])
            return
    #
    # Criar variáveis locais para melhorar legibilidade do código
    estado_do_jogador = estados[partidas[autor]['estado']]
    inventario_do_jogador = partidas[autor]['inventario']
    #
    # Varrer os possíveis próximos estados para validar com a mensagem do usuário
    for key, value in estado_do_jogador['proximos_estados'].items():
        if fullmatch(key, mensagem):
            #
            # Verificar se o jogador possui inventário mínimo para avançar
            if inventario_do_jogador.issuperset(estados[value]['inventario']):
                #
                # Atualiza o estado do jogador
                partidas[autor]['estado'] = value
                #
                # Remove os itens de inventário requisitados
                partidas[autor]['inventario'] = inventario_do_jogador.difference(
                    estados[value]['inventario'])
                #
                # Se houver um som referente ao estado,
                # toca no canal de voz do jogador
                if msg.channel.type.name != 'private':
                    arquivo_de_som = str(value) + '.mp3'
                    if exists(arquivo_de_som):
                        #
                        # Conectar no canal de áudio e emitir o som
                        som_opus = await discord.FFmpegOpusAudio.from_probe(arquivo_de_som)
                        canal_de_voz.play(som_opus)
                #
                # Se houver uma imagem referente ao estado, enviar
                arquivo_de_imagem = str(value) + '.png'
                if exists(arquivo_de_imagem):
                    await msg.channel.send(file=discord.File(arquivo_de_imagem))
                #
                # Criar uma lista de frases usando o delimitador '|' e enviar uma a uma
                [await msg.channel.send(i) for i in choice(estados[value]['frases']).split('|')]
            else:
                #
                # Retornar mensagem (e manter jogador no atual estado)
                await msg.channel.send(frases['inventario_insuficiente'])
            return
    #
    # Sempre responder ao usuário (dica ou não)
    if partidas[autor]['estado'] == 0:
        await msg.channel.send(choice(estado_do_jogador['frases']))
    else:
        await msg.channel.send(frases['erro'])

bot.run(getenv('DISCORD_TOKEN'))
