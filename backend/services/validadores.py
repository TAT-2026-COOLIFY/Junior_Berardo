import re

def validar_cnpj(cnpj: str) -> bool:
    cnpj_limpo = re.sub(r'\D', '', str(cnpj or ''))
    if len(cnpj_limpo) != 14 or cnpj_limpo == cnpj_limpo[0] * 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = sum(int(cnpj_limpo[i]) * pesos1[i] for i in range(12))
    resto1 = soma1 % 11
    digito1 = 0 if resto1 < 2 else 11 - resto1
    if int(cnpj_limpo[12]) != digito1:
        return False

    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma2 = sum(int(cnpj_limpo[i]) * pesos2[i] for i in range(13))
    resto2 = soma2 % 11
    digito2 = 0 if resto2 < 2 else 11 - resto2
    return int(cnpj_limpo[13]) == digito2