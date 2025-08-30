from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
import uuid
import bcrypt

# Inicializa a aplicação Flask
app = Flask(__name__)
app.secret_key = "minha_chave_secreta" #chave necessária para sessão

class Usuario:
    def __init__(self, nome, cpf, email, idade, senha, perfil, id=None):
        # Construtor: cria o objeto já com seus atributos
        self.id = id or str(uuid.uuid4())  # Se não for passado, gera um ID único
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.idade = idade
        self.senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.perfil = perfil #admin ou user

    def to_dict(self):
        """
        Transforma o objeto em dicionário.
        Esse método é necessário para salvar no JSON,
        já que JSON trabalha com dicionários/listas.
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email,
            "idade": self.idade,
            "senha": self.senha,
            "perfil": self.perfil
        }


class UsuarioRepository:
    ARQUIVO = "usuarios.json"

    @classmethod #decorator que transforma um método para receber a classe (cls) como primeiro parâmetro, sem instanciar um objeto
    def carregar(cls):
        """Carrega lista de usuários do arquivo JSON (READ)."""
        if os.path.exists(cls.ARQUIVO):
            with open(cls.ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    @classmethod
    def salvar(cls, usuarios):
        """Salva a lista de usuários no arquivo JSON (UPDATE/WRITE)."""
        with open(cls.ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4)

    @classmethod
    def adicionar(cls, usuario: Usuario):
        """Adiciona um novo usuário (CREATE)."""
        usuarios = cls.carregar()
        usuarios.append(usuario.to_dict())  # Converte objeto → dicionário
        cls.salvar(usuarios)

    @classmethod
    def deletar(cls, id):
        """Remove um usuário pelo ID (DELETE)."""
        usuarios = cls.carregar()
        filtrados = [u for u in usuarios if u["id"] != id]

        if len(usuarios) == len(filtrados):
            return False  # Nenhum usuário encontrado

        cls.salvar(filtrados)
        return True

    @classmethod
    def atualizar(cls, usuario_edit):
        """Atualiza os dados de um usuário (UPDATE)."""
        usuarios = cls.carregar()
        for u in usuarios:
            if u["id"] == usuario_edit.get("id"):
                u.update(usuario_edit)
                cls.salvar(usuarios)
                return True
        return False
    
    @classmethod
    def buscar_por_email(cls, email):
        usuarios = cls.carregar()
        for usuario in usuarios:
            if usuario["email"] == email:
                return usuario
        return None

@app.route("/")
def home():
    # View: renderiza o template HTML de cadastro
    return render_template("cadastro-usuario.html")

@app.route("/cadastro-usuario", methods=["POST"])
def cadastrar_usuario():
    """
    Rota de cadastro de usuário (CREATE).
    - Pega dados do formulário.
    - Cria um objeto Usuario.
    - Chama o repositório para salvar no JSON.
    """
    usuario = Usuario(
        nome=request.form.get("nome"),
        cpf=request.form.get("cpf"),
        email=request.form.get("email"),
        idade=request.form.get("idade"),
        senha=request.form.get("senha"),
        perfil=request.form.get("perfil")
    )

    UsuarioRepository.adicionar(usuario)
    return f"Usuário '{usuario.nome}' cadastrado com sucesso!"

@app.route("/login")
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = UsuarioRepository.buscar_por_email(email)
    if usuario and bcrypt.checkpw(senha.encode("utf-8"), usuario["senha"].encode("utf-8")):
        #salvar sessão
        session["id_usuario"] = usuario["id"]
        session["perfil"] = usuario["perfil"]
        return f"Login realizado com sucesso! Bem-vindo(a), {usuario['nome']}."
    
    return "Email ou senha inválidos", 401

@app.route("/logout")
def logout():
    if not session:
        return "O usuário não fez login"
    
    session.clear()
    return "Usuário deslogado!"

@app.route("/usuarios/json")
def buscar_usuarios_json():
    """
    Rota que retorna todos os usuários em JSON (READ).
    """

    if not session:
        return "O usuário não fez login", 400

    if session["perfil"] != "admin":
        return "Acesso negado. Área de admnistração"

    return jsonify(UsuarioRepository.carregar())


@app.route("/usuarios")
def buscar_usuarios():
    """
    Rota que renderiza a lista de usuários em HTML (READ).
    """
    if not session:
        return "O usuário não fez login", 400

    if session["perfil"] != "admin":
        return "Acesso negado. Área de admnistração"

    usuarios = UsuarioRepository.carregar()
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario(id):
    """
    Rota para excluir usuário pelo ID (DELETE).
    """
    if not session:
        return "O usuário não fez login", 400

    if session["perfil"] != "admin":
        return "Acesso negado. Área de administração"
        
    if UsuarioRepository.deletar(id):
        return jsonify({"mensagem": "Usuário deletado com sucesso."}), 200
    return jsonify({"erro": "Usuário não encontrado."}), 404

@app.route("/usuarios/", methods=["PUT"])
def atualizar_usuario():
    """
    Rota para atualizar dados de um usuário (UPDATE).
    """
    if not session:
        return "O usuário não fez login", 400

    if session["perfil"] != "admin":
        return "Acesso negado. Área de administração"
    
    usuario_edit = request.get_json()
    if UsuarioRepository.atualizar(usuario_edit):
        return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200
    
    return jsonify({"erro": "Não foi possível salvar as modificações"}), 404

@app.route("/admin")
def admin_area():
    if not session or session.get("perfil") != "admin":
        return redirect(url_for("home"))

if __name__ == "__main__":
    # Inicia o servidor Flask em modo debug
    app.run(debug=True)