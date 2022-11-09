frases = {
    'inventario_insuficiente': 'Sem os recursos necessários para avançar.',
    'canal_privado': 'Não é possível reproduzir áudio em canais privados.',
    'sem_canal_de_voz': 'Por favor, esteja em um canal de voz para ter a imersão completa do jogo.',
    'erro': 'I\'m sorry Dave, I\'m afraid I can\'t do that.'
}


estados = [
    {
        'estado': 0,
        'frases': ['Digite "iniciar" para começar o jogo.'],
        'proximos_estados': {
            '[iI]niciar?': 1
        }
    },
    {
        'estado': 1,
        'frases': ['Olá|!', 'Tudo bem,|como vai?'],
        'proximos_estados': {
            '[sS](i)+m': 2,
            '[nN][aã]+o': 3
        },
        'inventario': {}
    },
    {
        'estado': 2,
        'frases': ['Era uma vez...', 'E lá de volta|outra vez...'],
        'proximos_estados': {
            '[nN][aã]+o': 3
        },
        'inventario': {}
    },
    {
        'estado': 3,
        'frases': ['Fim do jogo!', 'Parabéns!'],
        'proximos_estados': {
            '[rR]einiciar?': 1
        },
        'inventario': {}
    }
]

partidas = []
