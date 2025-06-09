import unicodedata

def normalizar(texto):
    texto = str(texto).strip()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def capitalizar_nombre(nombre):
    return " ".join(nombre.strip().title().split())

def formato_clp(valor):
    try:
        return f"${int(valor):,}".replace(",", ".")
    except:
        return valor
