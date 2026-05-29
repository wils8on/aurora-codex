import streamlit as st
import json

st.title("📖 Biblioteca")

with open("data/livros.json", "r", encoding="utf-8") as file:
    livros = json.load(file)

favoritos = st.session_state.get("favoritos", [])

if favoritos:
    st.subheader("⭐ Favoritos")

    for livro in livros:
        if livro["id"] in favoritos:
            st.write(f"⭐ {livro['titulo']}")

    st.divider()

for livro in livros:
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])

        with col1:
            if livro["capa"]:
                st.image(
                    livro["capa"],
                    width="stretch"
                )

        with col2:
            st.subheader(livro["titulo"])

            st.caption(
                f"Autor: {livro['autor']} | Status: {livro['status']}"
            )

            st.write(livro["descricao"])

            if st.button(
                "Abrir livro",
                key=f"livro_{livro['id']}"
            ):
                st.session_state["livro_selecionado"] = livro["id"]
                st.switch_page("pages/4_Livro.py")

        st.divider()