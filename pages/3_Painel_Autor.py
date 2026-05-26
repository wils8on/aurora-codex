import streamlit as st
import json

st.title("✍️ Painel do Autor")

CAMINHO_LIVROS = "data/livros.json"

def carregar_livros():
    with open(CAMINHO_LIVROS, "r", encoding="utf-8") as file:
        return json.load(file)

def salvar_livros(livros):
    with open(CAMINHO_LIVROS, "w", encoding="utf-8") as file:
        json.dump(livros, file, ensure_ascii=False, indent=4)

livros = carregar_livros()

aba_livro, aba_capitulo = st.tabs([
    "📘 Cadastrar Livro",
    "📄 Cadastrar Capítulo"
])

with aba_livro:
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
                    "capitulos": []
                }

                livros.append(novo_livro)
                salvar_livros(livros)

                st.success("Livro cadastrado com sucesso.")

with aba_capitulo:
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

            titulo_capitulo = st.text_input("Título do capítulo")

            status_capitulo = st.selectbox(
                "Status do capítulo",
                ["Rascunho", "Publicado"]
            )

            conteudo_capitulo = st.text_area(
                "Conteúdo do capítulo",
                height=300
            )

            quantidade_palavras = len(conteudo_capitulo.split())

            st.caption(f"Palavras: {quantidade_palavras}")

            if st.button("Salvar capítulo"):
                if not titulo_capitulo or not conteudo_capitulo:
                    st.warning("Preencha o título e o conteúdo do capítulo.")
                else:
                    novo_numero = len(livro_escolhido["capitulos"]) + 1

                    novo_capitulo = {
                        "numero": novo_numero,
                        "titulo": titulo_capitulo,
                        "status": status_capitulo,
                        "conteudo": conteudo_capitulo
                    }

                    for livro in livros:
                        if livro["id"] == livro_escolhido["id"]:
                            livro["capitulos"].append(novo_capitulo)

                    salvar_livros(livros)

                    st.success("Capítulo salvo com sucesso.")