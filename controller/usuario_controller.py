from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from service.usuario_service import UsuarioService

usuario_bp = Blueprint("usuario", __name__)

@usuario_bp.route("/")
def home():
    return render_template("cadastro-usuario.html")

@usuario_bp.route("/login")
def login_get():
    return render_template("login.html")

@usuario_bp.route("/cadastro-usuario", methods=["POST"])
def cadastrar_usuario():
    dados = {
        "nome": request.form.get("nome"),
        "cpf": request.form.get("cpf"),
        "email": request.form.get("email"),
        "idade": request.form.get("idade"),
        "senha": request.form.get("senha"),
        "perfil": request.form.get("perfil", "user")
    }
    usuario = UsuarioService.cadastrar(dados)
    return f"Usuário '{usuario.nome}' cadastrado com sucesso!"

# ---------- LOGIN / LOGOUT ---------- #
@usuario_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = UsuarioService.autenticar(email, senha)
    if usuario:
        session["id_usuario"] = usuario["id"]
        session["perfil"] = usuario["perfil"]
        return f"Login realizado com sucesso! Bem-vindo, {usuario['nome']}."
    return "Email ou senha inválidos", 401

@usuario_bp.route("/logout")
def logout():
    session.clear()
    return "Usuário deslogado!"

# ---------- ROTAS PROTEGIDAS ---------- #
@usuario_bp.route("/usuarios/json")
def buscar_usuarios_json():
    if "id_usuario" not in session:
        return "Acesso negado. Faça login.", 401
    if session["perfil"] != "admin":
        return "Acesso negado. Área de administração.", 401
    return jsonify(UsuarioService.listar())

@usuario_bp.route("/usuarios")
def buscar_usuarios():
    if "id_usuario" not in session:
        return "Acesso negado. Faça login.", 401
    if session["perfil"] != "admin":
        return "Acesso negado. Área de administração.", 401
    usuarios = UsuarioService.listar()
    return render_template("usuarios.html", usuarios=usuarios)

@usuario_bp.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario(id):
    if session.get("perfil") != "admin":
        return "Acesso negado. Apenas administradores podem deletar usuários.", 403
    if UsuarioService.deletar(id):
        return jsonify({"mensagem": "Usuário deletado com sucesso."}), 200
    return jsonify({"erro": "Usuário não encontrado."}), 404

@usuario_bp.route("/usuarios/", methods=["PUT"])
def atualizar_usuario():
    if "id_usuario" not in session:
        return "Acesso negado. Faça login.", 401

    usuario_edit = request.get_json()
    if UsuarioService.atualizar(usuario_edit):
        return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200
    return jsonify({"erro": "Não foi possível salvar as modificações"}), 404

@usuario_bp.route("/admin")
def admin_area():
    if session.get("perfil") != "admin":
        return redirect(url_for("usuario.home"))
    return "Área do administrador"