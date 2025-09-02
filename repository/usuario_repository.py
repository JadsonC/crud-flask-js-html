import json
import os

class UsuarioRepository:
    ARQUIVO = "usuarios.json"

    @classmethod
    def carregar(cls):
        if os.path.exists(cls.ARQUIVO):
            with open(cls.ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    @classmethod
    def salvar(cls, usuarios):
        with open(cls.ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4)

    @classmethod
    def adicionar(cls, usuario):
        usuarios = cls.carregar()
        usuarios.append(usuario.to_dict())
        cls.salvar(usuarios)

    @classmethod
    def buscar_por_email(cls, email):
        usuarios = cls.carregar()
        for u in usuarios:
            if u["email"] == email:
                return u
        return None

    @classmethod
    def deletar(cls, id):
        usuarios = cls.carregar()
        filtrados = [u for u in usuarios if u["id"] != id]
        if len(usuarios) == len(filtrados):
            return False
        cls.salvar(filtrados)
        return True

    @classmethod
    def atualizar(cls, usuario_edit):
        usuarios = cls.carregar()
        for u in usuarios:
            if u["id"] == usuario_edit.get("id"):
                u.update(usuario_edit)
                cls.salvar(usuarios)
                return True
        return False