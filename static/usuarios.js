function excluirUsuario(id, cpf) {
    if (!confirm(`Tem certeza que deseja  excluir o usuário com o CPF ${cpf}?`)) {
        return
    }

    fetch(`/usuarios/${id}`, {
        method: 'DELETE'
    })
        .then(response => {
            return response.json().then(data => {
                if (!response.ok) {
                    throw new Error(data.erro || "Erro desconhecido")
                }
                return data;
            })
        })
        .then(data => {
            alert(data.mensagem);
            const linha = document.getElementById('linha-' + id)
            if (linha) linha.remove();
        })
        .catch(error => {
            console.error("Erro na requisição", error);
            alert("Errro ao excluir usuário" + error.message)
        })
}

function preencherFomulario(button) {
    var usuario = JSON.parse(button.getAttribute('data-usuario'))
    document.getElementById('id').value = usuario.id
    document.getElementById('nome').value = usuario.nome
    document.getElementById('email').value = usuario.email
    document.getElementById('idade').value = usuario.idade
    document.getElementById('cpf').value = usuario.cpf
}

function atualizarUsuario() {
    if (!confirm("Tem certeza que deseja alterar os dados do usuário?")) {
        return;
    }

    const form = document.getElementById("form-atualizar-usuario")

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const id = document.getElementById('id').value
        const nome = document.getElementById('nome').value
        const email = document.getElementById('email').value
        const idade = document.getElementById('idade').value
        const cpf = document.getElementById('cpf').value

        const usuario = {
            id: id,
            nome: nome,
            email: email,
            idade: idade,
            cpf: cpf
        }

        fetch(`/usuarios/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json" 
            },
            body: JSON.stringify(usuario)
        })
        .then(response => {
            response.json()
            alert("Usuário atualizado com sucesso!")
            location.reload();
        })
        .catch(error => {
            console.lerror("Erro ao atualizar", error)
        });
    });
}