from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from service.usuario_service import UsuarioService
from markupsafe import escape
from datetime import timedelta

usuario_bp = Blueprint("usuario", __name__)

@usuario_bp.route("/")
def home():
    return render_template("cadastro-usuario.html")

@usuario_bp.route("/login")
def login_get():
    return render_template("login.html")

# ---------- CADASTRO ---------- #
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
    status = UsuarioService.cadastrar(dados)
    if status:
        return f"Usuário '{dados['nome']}' cadastrado com sucesso!"
    else:
        return "Erro ao cadastrar usuário"

# ---------- LOGIN / JWT ---------- #
@usuario_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = UsuarioService.autenticar(email, senha)
    if not usuario:
        return jsonify({"erro": "Email ou senha inválidos"}), 401

    # Cria token com tempo de expiração (exemplo: 30 minutos)
    access_token = create_access_token(
        identity={"id": usuario["id"], "perfil": usuario["perfil"], "nome": usuario["nome"]},
        expires_delta=timedelta(minutes=30)
    )

    return jsonify({
        "mensagem": f"Login realizado com sucesso! Bem-vindo, {escape(usuario['nome'])}.",
        "token": access_token
    })

# ---------- ROTAS PROTEGIDAS ---------- #
@usuario_bp.route("/usuarios/json")
@jwt_required()
def buscar_usuarios_json():
    usuario_atual = get_jwt_identity()
    if usuario_atual["perfil"] != "admin":
        return jsonify({"erro": "Acesso negado. Área de administração."}), 403
    return jsonify(UsuarioService.listar())

@usuario_bp.route("/usuarios")
@jwt_required()
def buscar_usuarios():
    usuario_atual = get_jwt_identity()
    if usuario_atual["perfil"] != "admin":
        return jsonify({"erro": "Acesso negado. Área de administração."}), 403
    usuarios = UsuarioService.listar()
    return render_template("usuarios.html", usuarios=usuarios)

@usuario_bp.route("/usuarios/<id>", methods=["DELETE"])
@jwt_required()
def excluir_usuario(id):
    usuario_atual = get_jwt_identity()
    if usuario_atual["perfil"] != "admin":
        return jsonify({"erro": "Apenas administradores podem deletar usuários."}), 403
    if UsuarioService.deletar(id):
        return jsonify({"mensagem": "Usuário deletado com sucesso."}), 200
    return jsonify({"erro": "Usuário não encontrado."}), 404

@usuario_bp.route("/usuarios/", methods=["PUT"])
@jwt_required()
def atualizar_usuario():
    usuario_edit = request.get_json()
    if UsuarioService.atualizar(usuario_edit):
        return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200
    return jsonify({"erro": "Não foi possível salvar as modificações"}), 404

@usuario_bp.route("/admin")
@jwt_required()
def admin_area():
    usuario_atual = get_jwt_identity()
    if usuario_atual["perfil"] != "admin":
        return redirect(url_for("usuario.home"))
    return "Área do administrador"