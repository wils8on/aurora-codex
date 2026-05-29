import streamlit as st
import json
from pathlib import Path

st.title("📖 Biblioteca")

CAMINHO_LIVROS = "data/livros.json"

with open(CAMINHO_LIVROS, "r", encoding="utf-8") as file:
    livros = json.load(file)

historico_leitura = st.session_state.get("historico_leitura", {})
favoritos = st.session_state.get("favoritos", [])


# =========================
# 📊 Minha Leitura
# =========================

livros_iniciados = len(historico_leitura)

capitulos_concluidos = sum(
    historico_leitura.values()
)

livros_concluidos = 0
total_capitulos_existentes = 0

for livro in livros:
    total_capitulos = len(livro["capitulos"])
    total_capitulos_existentes += total_capitulos

    livro_id_str = str(livro["id"])

    if livro_id_str in historico_leitura:
        ultimo_lido = historico_leitura[livro_id_str]

        if ultimo_lido >= total_capitulos and total_capitulos > 0:
            livros_concluidos += 1

if total_capitulos_existentes > 0:
    progresso_geral = int(
        (
            capitulos_concluidos
            / total_capitulos_existentes
        ) * 100
    )
else:
    progresso_geral = 0

st.subheader("📊 Minha Leitura")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Livros iniciados",
    livros_iniciados
)

col2.metric(
    "Capítulos concluídos",
    capitulos_concluidos
)

col3.metric(
    "Livros concluídos",
    livros_concluidos
)

col4.metric(
    "Progresso geral",
    f"{progresso_geral}%"
)

st.divider()


# =========================
# 📚 Continuar lendo
# =========================

st.subheader("📚 Continuar lendo")

livros_em_andamento = []

for livro in livros:
    livro_id_str = str(livro["id"])

    if livro_id_str in historico_leitura:
        ultimo_capitulo = historico_leitura[livro_id_str]

        if ultimo_capitulo > 0:
            livros_em_andamento.append(
                {
                    "livro": livro,
                    "ultimo_capitulo": ultimo_capitulo
                }
            )

if livros_em_andamento:
    for item in livros_em_andamento:
        livro = item["livro"]
        ultimo_capitulo = item["ultimo_capitulo"]
        total_capitulos = len(livro["capitulos"])

        with st.container(border=True):
            col1, col2 = st.columns([1, 3])

            with col1:
                capa = livro.get("capa", "")

                if capa and Path(capa).exists():
                    st.image(capa, width="stretch")

            with col2:
                st.write(f"📘 **{livro['titulo']}**")

                if total_capitulos > 0:
                    progresso = min(
                        ultimo_capitulo / total_capitulos,
                        1
                    )

                    percentual = int(progresso * 100)

                    st.caption(
                        f"Capítulo {ultimo_capitulo} de {total_capitulos} | {percentual}% concluído"
                    )

                    st.progress(progresso)

                    if ultimo_capitulo >= total_capitulos:
                        st.success("Livro concluído")

                else:
                    st.caption("Nenhum capítulo disponível ainda.")
                    progresso = 0

                if st.button(
                    "Continuar",
                    key=f"continuar_{livro['id']}"
                ):
                    st.session_state["livro_selecionado"] = livro["id"]
                    st.session_state["capitulo_index"] = max(
                        ultimo_capitulo - 1,
                        0
                    )
                    st.switch_page("pages/2_Leitura.py")

else:
    st.info("Nenhuma leitura iniciada ainda.")

st.divider()


# =========================
# ⭐ Favoritos
# =========================

if favoritos:
    st.subheader("⭐ Favoritos")

    for livro in livros:
        if livro["id"] in favoritos:
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])

                with col1:
                    capa = livro.get("capa", "")

                    if capa and Path(capa).exists():
                        st.image(capa, width="stretch")

                with col2:
                    st.write(f"⭐ **{livro['titulo']}**")
                    st.caption(
                        f"Autor: {livro['autor']} | Status: {livro['status']}"
                    )

                    if st.button(
                        "Abrir favorito",
                        key=f"favorito_{livro['id']}"
                    ):
                        st.session_state["livro_selecionado"] = livro["id"]
                        st.switch_page("pages/4_Livro.py")

    st.divider()


# =========================
# 📚 Todos os livros
# =========================

st.subheader("📚 Todos os livros")

for livro in livros:
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])

        with col1:
            capa = livro.get("capa", "")

            if capa and Path(capa).exists():
                st.image(capa, width="stretch")

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