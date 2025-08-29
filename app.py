from flask import Flask, render_template, request, jsonify
import os
import json
import uuid

app = Flask(__name__)

def salvar_usuario(usuario):
    usuarios = carregar_usuarios()

    try:
        usuarios.append(usuario)

        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
        
        return True
    except:
        return False

def carregar_usuarios():
    try:
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        else:
            return []
    except:
        return []

def deletar_usuario(id):
    usuarios = carregar_usuarios()
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.get("id") != id]

    if len(usuarios) == len(usuarios_filtrados):
        return False
    
    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios_filtrados, arquivo, indent=4)
        return True
    except:
        return False
    
@app.route("/")
def home():
    return render_template("cadastro-usuario.html")

@app.route("/cadastro-usuario", methods=["POST"])
def cadastrar_usuario():
    nome = request.form.get("nome")
    email = request.form.get("email")
    idade = request.form.get("idade")
    cpf = request.form.get("cpf")
    senha = request.form.get("senha")

    #criando um dicionário 
    usuario = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "email": email,
        "cpf": cpf,
        "senha": senha,
        "idade": idade
    }

    status = salvar_usuario(usuario)

    if(status):
       return f"Usuário '{usuario["nome"]}' cadastrado com sucesso!" 
    else:
        return "Não foi possível cadastrar o usuário!"

@app.route("/usuarios/json")
def buscar_usuarios_json():
    usuarios = carregar_usuarios()
    return jsonify(usuarios)

@app.route("/usuarios")
def buscar_usuarios():
    usuarios = carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario(id):
    sucesso = deletar_usuario(id)

    if sucesso:
        return jsonify({"mensagem": "Usuário deletado com sucesso"}), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404

@app.route("/usuarios/", methods=["PUT"])
def atualizar_usuario():
    usuario_edit = request.get_json()
    usuario_edit = dict(usuario_edit)

    usuarios = carregar_usuarios()

    for usuario in usuarios:
        if usuario.get("id") == usuario_edit.get("id"):
            usuario.update(usuario_edit)
            break
    
    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)

        return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200 
    except:
        return jsonify({"erro": "Não foi possível salvar as modificações"}), 404 


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
