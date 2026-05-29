from datetime import datetime
import streamlit as st
import json

from auth import verificar_login

if not verificar_login():
    st.stop()

st.title("✍️ Painel do Autor")

CAMINHO_LIVROS = "data/livros.json"
CAMINHO_HISTORICO = "data/historico.json"


def carregar_livros():
    with open(CAMINHO_LIVROS, "r", encoding="utf-8") as file:
        return json.load(file)


def salvar_livros(livros):
    with open(CAMINHO_LIVROS, "w", encoding="utf-8") as file:
        json.dump(livros, file, ensure_ascii=False, indent=4)


def carregar_historico():
    try:
        with open(CAMINHO_HISTORICO, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def salvar_historico(historico):
    with open(CAMINHO_HISTORICO, "w", encoding="utf-8") as file:
        json.dump(historico, file, ensure_ascii=False, indent=4)


def registrar_historico(acao, livro, capitulo, detalhes):
    historico = carregar_historico()

    novo_registro = {
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "acao": acao,
        "livro": livro,
        "capitulo": capitulo,
        "detalhes": detalhes
    }

    historico.insert(0, novo_registro)
    salvar_historico(historico)


def voltar_dashboard(mensagem):
    st.session_state["mensagem_dashboard"] = mensagem
    st.session_state["ir_para_dashboard"] = True
    st.rerun()


livros = carregar_livros()

if st.session_state.get("ir_para_dashboard"):
    st.session_state["opcao_painel"] = "📊 Dashboard"
    del st.session_state["ir_para_dashboard"]

opcao_painel = st.radio(
    "Menu do Painel",
    [
        "📊 Dashboard",
        "📘 Cadastrar Livro",
        "📄 Cadastrar Capítulo",
        "✏️ Editar Capítulo",
        "🗑️ Excluir Capítulo",
        "🕘 Histórico"
    ],
    horizontal=True,
    key="opcao_painel"
)


if opcao_painel == "📊 Dashboard":
    if "mensagem_dashboard" in st.session_state:
        st.success(st.session_state["mensagem_dashboard"])
        del st.session_state["mensagem_dashboard"]

    st.subheader("Visão geral do Aurora Codex")

    total_livros = len(livros)

    total_capitulos = sum(
        len(livro["capitulos"]) for livro in livros
    )

    total_favoritos = len(
        st.session_state.get("favoritos", [])
    )

    capitulos_publicados = sum(
        1
        for livro in livros
        for capitulo in livro["capitulos"]
        if capitulo["status"] == "Publicado"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Livros", total_livros)
    col2.metric("Capítulos", total_capitulos)
    col3.metric("Publicados", capitulos_publicados)
    col4.metric("Favoritos", total_favoritos)

    st.divider()

    st.subheader("Obras cadastradas")

    for livro in livros:
        with st.container(border=True):
            st.write(f"📘 **{livro['titulo']}**")
            st.caption(
                f"Status: {livro['status']} | Capítulos: {len(livro['capitulos'])}"
            )


elif opcao_painel == "📘 Cadastrar Livro":
    st.subheader("Novo livro")

    with st.container(border=True):
        titulo_livro = st.text_input("Título do livro")
        autor_livro = st.text_input("Autor", value="Ison W. Lone")

        status_livro = st.selectbox(
            "Status",
            ["Rascunho", "Em publicação", "Finalizado"]
        )

        descricao_livro = st.text_area(
            "Descrição do livro",
            height=150
        )

        if st.button("Salvar livro"):
            if not titulo_livro or not descricao_livro:
                st.warning("Preencha o título e a descrição do livro.")
            else:
                novo_id = max([livro["id"] for livro in livros], default=0) + 1

                novo_livro = {
                    "id": novo_id,
                    "titulo": titulo_livro,
                    "autor": autor_livro,
                    "status": status_livro,
                    "descricao": descricao_livro,
                    "capa": "",
                    "banner": "",
                    "capitulos": []
                }

                livros.append(novo_livro)
                salvar_livros(livros)

                registrar_historico(
                    "Cadastro de livro",
                    titulo_livro,
                    "-",
                    f"Livro criado com status: {status_livro}."
                )

                voltar_dashboard(
                    f"Livro '{titulo_livro}' cadastrado com sucesso."
                )


elif opcao_painel == "📄 Cadastrar Capítulo":
    st.subheader("Novo capítulo")

    if not livros:
        st.warning("Cadastre um livro primeiro.")
    else:
        with st.container(border=True):
            livro_escolhido = st.selectbox(
                "Escolha o livro",
                livros,
                format_func=lambda livro: livro["titulo"]
            )

            numero_sugerido = len(livro_escolhido["capitulos"]) + 1

            numero_capitulo = st.number_input(
                "Número do capítulo",
                min_value=1,
                value=numero_sugerido,
                step=1
            )

            titulo_capitulo = st.text_input("Título do capítulo")

            status_capitulo = st.selectbox(
                "Status do capítulo",
                ["Rascunho", "Publicado"]
            )

            conteudo_capitulo = st.text_area(
                "Conteúdo do capítulo",
                height=400
            )

            st.caption(f"Palavras: {len(conteudo_capitulo.split())}")

            if st.button("Salvar capítulo"):
                if not titulo_capitulo or not conteudo_capitulo:
                    st.warning("Preencha o título e o conteúdo do capítulo.")
                else:
                    novo_capitulo = {
                        "numero": int(numero_capitulo),
                        "titulo": titulo_capitulo,
                        "status": status_capitulo,
                        "conteudo": conteudo_capitulo
                    }

                    for livro in livros:
                        if livro["id"] == livro_escolhido["id"]:
                            livro["capitulos"].append(novo_capitulo)

                            livro["capitulos"] = sorted(
                                livro["capitulos"],
                                key=lambda capitulo: capitulo["numero"]
                            )

                    salvar_livros(livros)

                    registrar_historico(
                        "Cadastro de capítulo",
                        livro_escolhido["titulo"],
                        f"Capítulo {numero_capitulo} - {titulo_capitulo}",
                        f"Capítulo cadastrado com status: {status_capitulo}."
                    )

                    voltar_dashboard(
                        f"Capítulo '{titulo_capitulo}' cadastrado com sucesso."
                    )


elif opcao_painel == "✏️ Editar Capítulo":
    st.subheader("Editar capítulo")

    if not livros:
        st.warning("Nenhum livro cadastrado.")
    else:
        livro_edicao = st.selectbox(
            "Escolha o livro para edição",
            livros,
            format_func=lambda livro: livro["titulo"],
            key="livro_edicao"
        )

        if not livro_edicao["capitulos"]:
            st.warning("Este livro ainda não possui capítulos.")
        else:
            capitulo_edicao = st.selectbox(
                "Escolha o capítulo",
                livro_edicao["capitulos"],
                format_func=lambda capitulo: f"Capítulo {capitulo['numero']} - {capitulo['titulo']}",
                key="capitulo_edicao"
            )

            with st.container(border=True):
                novo_numero = st.number_input(
                    "Número do capítulo",
                    min_value=1,
                    value=int(capitulo_edicao["numero"]),
                    step=1
                )

                novo_titulo = st.text_input(
                    "Título do capítulo",
                    value=capitulo_edicao["titulo"]
                )

                novo_status = st.selectbox(
                    "Status",
                    ["Rascunho", "Publicado"],
                    index=["Rascunho", "Publicado"].index(capitulo_edicao["status"])
                )

                novo_conteudo = st.text_area(
                    "Conteúdo",
                    value=capitulo_edicao["conteudo"],
                    height=400
                )

                st.caption(f"Palavras: {len(novo_conteudo.split())}")

                if st.button("Salvar alterações"):
                    alteracoes = []

                    if int(novo_numero) != int(capitulo_edicao["numero"]):
                        alteracoes.append(
                            f"Número alterado de {capitulo_edicao['numero']} para {novo_numero}"
                        )

                    if novo_titulo != capitulo_edicao["titulo"]:
                        alteracoes.append(
                            f"Título alterado de '{capitulo_edicao['titulo']}' para '{novo_titulo}'"
                        )

                    if novo_status != capitulo_edicao["status"]:
                        alteracoes.append(
                            f"Status alterado de '{capitulo_edicao['status']}' para '{novo_status}'"
                        )

                    if novo_conteudo != capitulo_edicao["conteudo"]:
                        alteracoes.append("Conteúdo do capítulo atualizado")

                    if not alteracoes:
                        alteracoes.append("Nenhuma alteração relevante identificada")

                    titulo_original = capitulo_edicao["titulo"]
                    numero_original = capitulo_edicao["numero"]

                    for livro in livros:
                        if livro["id"] == livro_edicao["id"]:
                            for capitulo in livro["capitulos"]:
                                if capitulo["numero"] == capitulo_edicao["numero"]:
                                    capitulo["numero"] = int(novo_numero)
                                    capitulo["titulo"] = novo_titulo
                                    capitulo["status"] = novo_status
                                    capitulo["conteudo"] = novo_conteudo

                            livro["capitulos"] = sorted(
                                livro["capitulos"],
                                key=lambda capitulo: capitulo["numero"]
                            )

                    salvar_livros(livros)

                    registrar_historico(
                        "Edição de capítulo",
                        livro_edicao["titulo"],
                        f"Capítulo {numero_original} - {titulo_original}",
                        " | ".join(alteracoes)
                    )

                    voltar_dashboard(
                        f"Capítulo '{novo_titulo}' atualizado com sucesso."
                    )


elif opcao_painel == "🗑️ Excluir Capítulo":
    st.subheader("Excluir capítulo")

    if not livros:
        st.warning("Nenhum livro cadastrado.")
    else:
        livro_exclusao = st.selectbox(
            "Escolha o livro",
            livros,
            format_func=lambda livro: livro["titulo"],
            key="livro_exclusao"
        )

        if not livro_exclusao["capitulos"]:
            st.warning("Este livro ainda não possui capítulos.")
        else:
            capitulo_exclusao = st.selectbox(
                "Escolha o capítulo para excluir",
                livro_exclusao["capitulos"],
                format_func=lambda capitulo: f"Capítulo {capitulo['numero']} - {capitulo['titulo']}",
                key="capitulo_exclusao"
            )

            st.error(
                f"Você está prestes a excluir: Capítulo {capitulo_exclusao['numero']} - {capitulo_exclusao['titulo']}"
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir este capítulo."
            )

            if st.button("Excluir capítulo"):
                if not confirmar:
                    st.warning("Marque a confirmação antes de excluir.")
                else:
                    titulo_excluido = capitulo_exclusao["titulo"]
                    numero_excluido = capitulo_exclusao["numero"]

                    for livro in livros:
                        if livro["id"] == livro_exclusao["id"]:
                            livro["capitulos"] = [
                                capitulo
                                for capitulo in livro["capitulos"]
                                if capitulo["numero"] != capitulo_exclusao["numero"]
                            ]

                    salvar_livros(livros)

                    registrar_historico(
                        "Exclusão de capítulo",
                        livro_exclusao["titulo"],
                        f"Capítulo {numero_excluido} - {titulo_excluido}",
                        "Capítulo removido do livro."
                    )

                    voltar_dashboard(
                        f"Capítulo '{titulo_excluido}' excluído com sucesso."
                    )


elif opcao_painel == "🕘 Histórico":
    st.subheader("Histórico de alterações")

    historico = carregar_historico()

    if not historico:
        st.info("Nenhuma alteração registrada ainda.")
    else:
        for item in historico:
            with st.container(border=True):
                st.write(f"**{item['acao']}**")
                st.caption(item["data_hora"])
                st.write(f"Livro: {item['livro']}")
                st.write(f"Capítulo: {item['capitulo']}")
                st.write(item["detalhes"])