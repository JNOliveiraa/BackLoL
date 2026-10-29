from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

import database
import schemas

app = FastAPI(title="LoL Client Backend API")

# permite que o repositorio do React acesse esse servidor via fetch
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configuração da criptografia de senha (segurança)
pwd_context = CryptContext(schemes =["bcrypt"], deprecated="auto")

# Chave secreta para criptografar o token JWT (pode ser qualquer texto)
SECRET_KEY = "sua_chave_secreta_hextech_do_lol"
ALGORITHM = "HS256"

@app.get("/")
def home():
    return {"status": "Servidor do LoL Client rodando com sucesso!"}


# 🚀 ROTA 1: Cadastro de usuarios
@app.post("/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: schemas.UsuarioCadastro):
    conn = database.get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro ao conectar com o banco de dados")

    cursor = conn.cursor()

    # Verifica se o usuario ou email ja existem 
    cursor.execute("SELECT id FROM usuarios WHERE username = %s OR email = %s;", (usuario.username, usuario.email))
    usuario_existente = cursor.fetchone()

    if usuario_existente:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Nome de usuario ou email ja cadastrados")

    # Criptografa a senha antes de salvar
    senha_criptografada = pwd_context.hash(usuario.senha)

    try:
        cursor.execute(
            "INSERT INTO usuarios (username, email, senha) VALUES (%s, %s, %s) RETURNING id;",
            (usuario.username, usuario.email, senha_criptografada)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensagem": "Conta criada com sucesso!", "username": usuario.username}
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Erro interno ao salvar dados: {e}")

    


# 🚀 NOVA ROTA: Login de Usuarios (Geração do Token)
@app.post("/login")
def login_usuario(usuario: schemas.UsuarioLogin):
    conn = database.get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro ao conectar com o banco de dados")

    cursor = conn.cursor()

    # 1. Busca o usuário pelo username na tabela do PostgreSQL
    cursor.execute("SELECT id, username, senha, level, blue_essence, riot_points FROM usuarios WHERE username = %s;", (usuario.username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # 2 se o usuario não existir ou a senha estiver errada, barra a entrada
    if not user or not pwd_context.verify(usuario.senha, user["senha"]):
        raise HTTPException(status_code=401, detail="Nome de usuário ou senha incorretos")

    #. Cria o Token de Acesso Válido por 2horas
    tempo_expiracao = datetime.utcnow() + timedelta(hours=2)
    dados_do_token = {
        "sub": user["username"],
        "exp": tempo_expiracao,
        "level": user["level"],
        "blue_essence": user["blue_essence"],
        "riot_points": user["riot_points"]
    }

    token_jwt = jwt.encode(dados_do_token, SECRET_KEY, algorithm=ALGORITHM)

    # 4. Retorna o token de sucesso e os dados básicos para o front-end
    return {
        "access_token": token_jwt,
        "token_type": "bearer",
        "username": user["username"]
    }
