import discord
from discord.ext import commands

# Configurações
TOKEN = 'MTAwMzQyMzYwMTk3MTY5NTc4Nw.G7h4hM.CI3Pg15dCILXYxw5J1gjixsBRtllWUHTO4BYTQ'  # Substitua 'seu_token_aqui' pelo token do seu bot
PREFIX = '!'  # Prefixo de comando do bot
FORM_CHANNEL_ID = 1202368060913094729  # ID do canal onde as respostas do formulário serão enviadas

FORM_FIELDS = [
    "Nome",
    "Idade",
    "E-mail",
    "Telefone"
]

# Variável global para armazenar o ID da mensagem original do formulário de admissão
form_message_ids = {}

# Inicialização do bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    print('Pronto para receber formulários de admissão.')


@bot.command()
async def enviarformulario(ctx):
    # Envia as instruções
    embed = discord.Embed(title="Formulário de Admissão",
                          description="Por favor, preencha o formulário abaixo com as informações solicitadas:",
                          color=discord.Color.blue())
    # Adiciona campos vazios ao embed para cada campo do formulário
    for field in FORM_FIELDS:
        embed.add_field(name=field, value="Digite sua resposta aqui", inline=False)
    message = await ctx.send(embed=embed)

    # Inicializa as respostas
    respostas = {}

    # Atualiza o embed com as respostas fornecidas
    for field in FORM_FIELDS:
        await ctx.send(f"Por favor, digite sua resposta para {field}:")
        response = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        respostas[field] = response.content
        # Atualiza o embed com a resposta fornecida
        embed.set_field_at(FORM_FIELDS.index(field), name=field, value=response.content)

        await message.edit(embed=embed)

    # Constrói uma mensagem com as respostas
    response_message = f"Respostas do formulário de {ctx.author.mention}:\n"  # Menciona o autor do formulário
    for field, answer in respostas.items():
        response_message += f"{field}: {answer}\n"

    # Envia as respostas do formulário para o canal específico
    channel = bot.get_channel(FORM_CHANNEL_ID)
    if channel:
        form_message = await channel.send(response_message)
        # Armazena o ID da mensagem original do formulário de admissão
        form_message_ids[form_message.id] = ctx.author.id
        # Adiciona reações à mensagem do formulário
        await form_message.add_reaction('✅')  # Reação de confirmação
        await form_message.add_reaction('❌')  # Reação de negação
        await ctx.send("Seu formulário foi enviado com sucesso. Aguarde uma resposta.")
    else:
        await ctx.send(f'Não foi possível enviar o formulário no momento. Por favor, tente novamente mais tarde.')


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if reaction.message.channel.id == FORM_CHANNEL_ID:
        # Verifica se a mensagem original do formulário de admissão está registrada
        if reaction.message.id in form_message_ids:
            author_id = form_message_ids[reaction.message.id]
            author = await bot.fetch_user(author_id)
            if str(reaction.emoji) == '✅':
                await author.send("Parabéns! Sua admissão foi aceita. Bem-vindo à nossa comunidade!")
            elif str(reaction.emoji) == '❌':
                await author.send("Sua admissão foi recusada. Entre em contato conosco para mais informações.")


bot.run(TOKEN)