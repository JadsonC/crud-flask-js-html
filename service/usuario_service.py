from model.usuario import Usuario
from repository.usuario_repository import UsuarioRepository
import bcrypt

class UsuarioService:
    # 🔹 O @staticmethod indica que este método é "estático",
    # ou seja, pode ser chamado sem precisar criar um objeto da classe UsuarioService e
    # sem precisar utilizar atributos da classe
    # Exemplo: UsuarioService.cadastrar(dados)
    @staticmethod
    # ** pega cada chave do dicionário e envia como se fosse um parâmetro nomeado para o construtor da classe Usuario.
        # Exemplo: usuario = Usuario(nome="Ana", cpf="12345678900", email="ana@email.com", idade=25, senha="1234", perfil="user")
    def cadastar(dados):
        usuario = Usuario(**dados)

    @staticmethod
    def autenticar(email, senha):
        usuario = UsuarioRepository.buscar_por_email(email)
        if usuario and bcrypt.checkpw(senha.encode("utf-8"), usuario["senha"].encode("utf-8")):
            return usuario
        return None

    @staticmethod
    def atualizar(usuario_edit):
        return UsuarioRepository.atualizar(usuario_edit)
    
    @staticmethod
    def deletar(id):
        return UsuarioRepository.deletar(id)

    @staticmethod
    def listar():
        return UsuarioRepository.carregar()