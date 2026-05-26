import streamlit as st
import json

# Título
st.title("📚 Leitura")

# Abrindo os livros
with open("data/livros.json", "r", encoding="utf-8") as file:
    livros = json.load(file)

# Pegando livro salvo
livro_id = st.session_state.get("livro_selecionado")

# Se nenhum livro foi escolhido
if livro_id is None:

    st.warning("Nenhum livro selecionado.")

# Se existe livro selecionado
else:

    # Encontrando livro
    livro = next(
        (l for l in livros if l["id"] == livro_id),
        None
    )

    # Caso encontre
    if livro:

        st.header(livro["titulo"])

        # Lista de capítulos
        capitulos = livro["capitulos"]

        # Escolha do capítulo
        capitulo = st.selectbox(
            "Escolha o capítulo",
            capitulos,
            format_func=lambda c:
                f"Capítulo {c['numero']} - {c['titulo']}"
        )

        st.divider()

        col1, col2 = st.columns([4,1])

        with col1:
            st.subheader(capitulo["titulo"])

        with col2:
            st.info(capitulo["status"])

        st.markdown(
            f"""
            <div style="
                max-width: 850px;
                font-size: 18px;
                line-height: 1.8;
                text-align: justify;
                padding: 24px;
                border-radius: 16px;
                background-color: rgba(255,255,255,0.04);
            ">
                {capitulo["conteudo"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.error("Livro não encontrado.")