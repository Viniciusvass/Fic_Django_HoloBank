import random
from datetime import date

def gerar_numero_cartao():
    return ''.join(str(random.randint(0, 9)) for _ in range(16))

def gerar_cvv():
    return ''.join(str(random.randint(0, 9)) for _ in range(3))

def gerar_validade():
    hoje = date.today()
    return hoje.replace(year=hoje.year + 5)

def gerar_senha():
    return ''.join(str(random.randint(0, 9)) for _ in range(4))
