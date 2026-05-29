import streamlit as st
import json
from pathlib import Path

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
        banner = livro.get("banner", "")

        if banner and Path(banner).exists():
            st.image(
                banner,
                width="stretch"
            )
            st.divider()

        elif banner:
            st.warning(f"Banner não encontrado: {banner}")

        col1, col2 = st.columns([1, 2])

        with col1:
            capa = livro.get("capa", "")

            if capa and Path(capa).exists():
                st.image(
                    capa,
                    width="stretch"
                )

            elif capa:
                st.warning(f"Capa não encontrada: {capa}")

        with col2:
            st.header(livro["titulo"])

            favoritos = st.session_state.get("favoritos", [])
            favoritado = livro["id"] in favoritos

            if favoritado:
                if st.button("⭐ Favoritado"):
                    favoritos.remove(livro["id"])
                    st.session_state["favoritos"] = favoritos
                    st.rerun()
            else:
                if st.button("☆ Favoritar"):
                    favoritos.append(livro["id"])
                    st.session_state["favoritos"] = favoritos
                    st.rerun()

            st.caption(f"Autor: {livro['autor']} | Status: {livro['status']}")
            st.write(livro["descricao"])

            st.divider()

            total_capitulos = len(livro["capitulos"])

            if "historico_leitura" not in st.session_state:
                st.session_state["historico_leitura"] = {}

            historico_leitura = st.session_state["historico_leitura"]

            livro_id_str = str(livro_id)

            ultimo_capitulo = historico_leitura.get(
                livro_id_str,
                0
            )

            if total_capitulos > 0:
                progresso = min(
                    ultimo_capitulo / total_capitulos,
                    1
                )
            else:
                progresso = 0

            st.metric("Capítulos", total_capitulos)

            st.markdown("### Progresso da leitura")

            st.progress(progresso)

            percentual = int(progresso * 100)

            st.metric(
                "Progresso",
                f"{percentual}%"
            )

            st.caption(
                f"{ultimo_capitulo} de {total_capitulos} capítulos"
            )

            if total_capitulos > 0:
                if ultimo_capitulo:
                    st.info(f"Último capítulo concluído: {ultimo_capitulo}")

                    if st.button("Continuar leitura"):
                        st.session_state["capitulo_index"] = ultimo_capitulo - 1
                        st.switch_page("pages/2_Leitura.py")

                if st.button("Começar do início"):
                    st.session_state["capitulo_index"] = 0
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