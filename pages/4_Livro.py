import streamlit as st
import json

st.title("🌌 Livro")

CAMINHO_LIVROS = "data/livros.json"

with open(CAMINHO_LIVROS, "r", encoding="utf-8") as file:
    livros = json.load(file)

livro_id = st.session_state.get("livro_selecionado")

if livro_id is None:
    st.warning("Nenhum livro selecionado. Volte para a Biblioteca.")

else:
    livro = next(
        (l for l in livros if l["id"] == livro_id),
        None
    )

    if livro is None:
        st.error("Livro não encontrado.")

    else:
        if livro.get("banner"):
            st.image(
                livro["banner"],
                use_container_width=True
            )

            st.divider()

        col1, col2 = st.columns([1, 2])

        with col1:
            if livro.get("capa"):
                st.image(
                    livro["capa"],
                    use_container_width=True
                )

        with col2:
            st.header(livro["titulo"])
            st.caption(f"Autor: {livro['autor']} | Status: {livro['status']}")
            st.write(livro["descricao"])

            st.divider()

            total_capitulos = len(livro["capitulos"])

            st.metric("Capítulos", total_capitulos)

            if total_capitulos > 0:
                if st.button("Começar leitura"):
                    st.switch_page("pages/2_Leitura.py")
            else:
                st.warning("Este livro ainda não possui capítulos publicados.")

        st.divider()

        st.subheader("📄 Capítulos")

        if livro["capitulos"]:
            for capitulo in livro["capitulos"]:
                with st.container(border=True):
                    st.write(
                        f"Capítulo {capitulo['numero']} - {capitulo['titulo']}"
                    )
                    st.caption(f"Status: {capitulo['status']}")
        else:
            st.info("Nenhum capítulo cadastrado ainda.")