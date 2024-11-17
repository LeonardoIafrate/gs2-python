import re
from datetime import datetime
from bd.connection import *
from fastapi import HTTPException


def valida_eficiencia(eficiencia):
    eficiencias = ["A", "B", "C", "D", "E", "F", "G"]
    if eficiencia in eficiencias:
        return True
    else:
        return False
    

def valida_data_nascimento(data_nascimento: str):
    try:
        data = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        
        if 1920 <= data.year <= 2011:
            return True
        else:
            print("O ano deve estar entre 1920 e 2011.")
            return False
    except ValueError:
        print("Data inválida. Use o formato DD-MM-AAAA.")
        return False


def valida_email(test_str = "leonardoiafrate01@gmail.com"):
    regex = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    return bool(re.search(regex, test_str))
    

def valida_senha(senha):
    if len(senha) < 8:
        print("senha mt curta")
        return False
    if not re.search(r'[A-Z]', senha):
        print("Senha deve conter uma letra maiúscula")
        return False
    if not re.search(r'[a-z]', senha):
        print("Senha deve conter uma letra minúscula")
        return False
    if not re.search(r'[0-9]', senha):
        print("Senha não possui número")
        return False
    if not re.search(r'[!@#$%&*()[{};,.:/\|]', senha):
        print("Senha não possuí caracter especial")
        return False
    return True


def valida_cpf(cpf="123.456.789-01"):
    regex = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$"

    if not re.match(regex, cpf):
        return None
    
    cpf_numerico = cpf.replace(".", "").replace("-", "")

    return cpf_numerico

def valida_nome(nome : str):
    if nome.replace(" ", "").isalpha():
        return True
    else:
        return False

def valida_endereco(endereco: str):
    if endereco.replace(" ", "").isalnum:
        return True
    else:
        return False