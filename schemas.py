from pydantic import BaseModel

# Modelo de dados para quando um usuario for se cadastrar

class UsuarioCadastro(BaseModel):
  usename: str
  email: str
  senha: str


# Modelo de dados para quando o usuario for fazer login
class UsuarioLogin(BaseModel):
  username: str
  senha: str