from utils import carregar_leitor

import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="Aurora Codex",
    page_icon="🌌",
    layout="wide"
)

CAMINHO_LIVROS = "data/livros.json"
CAMINHO_LEITURAS = "data/leituras.json"

with open(CAMINHO_LIVROS, "r", encoding="utf-8") as file:
    livros = json.load(file)

try:
    with open(CAMINHO_LEITURAS, "r", encoding="utf-8") as file:
        leituras = json.load(file)
except FileNotFoundError:
    leituras = []

dados_leitor = carregar_leitor()

historico_leitura = dados_leitor["historico_leitura"]
favoritos = dados_leitor["favoritos"]


def imagem_existe(caminho):
    return caminho and Path(caminho).exists()


def abrir_livro(livro):
    st.session_state["livro_selecionado"] = livro["id"]
    st.switch_page("pages/4_Livro.py")


def continuar_livro(livro, ultimo_capitulo):
    st.session_state["livro_selecionado"] = livro["id"]
    st.session_state["capitulo_index"] = max(ultimo_capitulo - 1, 0)
    st.switch_page("pages/2_Leitura.py")


def abrir_capitulo(livro, indice_capitulo):
    st.session_state["livro_selecionado"] = livro["id"]
    st.session_state["capitulo_index"] = indice_capitulo
    st.switch_page("pages/2_Leitura.py")


# =========================
# HERO
# =========================

livro_destaque = next(
    (
        livro
        for livro in livros
        if imagem_existe(livro.get("banner", ""))
    ),
    None
)

st.title("🌌 Aurora Codex")

if livro_destaque:
    banner = livro_destaque.get("banner", "")

    st.image(banner, width="stretch")

    st.markdown(
        f"""
        ### Destaque: {livro_destaque["titulo"]}

        {livro_destaque["descricao"]}
        """
    )

    col_hero_1, col_hero_2 = st.columns([1, 5])

    with col_hero_1:
        if st.button("📖 Ler destaque"):
            abrir_livro(livro_destaque)

    with col_hero_2:
        if st.button("📚 Explorar Biblioteca"):
            st.switch_page("pages/1_Biblioteca.py")

else:
    st.markdown(
        """
        ### Sua biblioteca digital de histórias

        Continue suas leituras, descubra novas obras
        e acompanhe sua jornada literária.
        """
    )

    if st.button("📚 Explorar Biblioteca"):
        st.switch_page("pages/1_Biblioteca.py")

st.divider()


# =========================
# ESTATÍSTICAS GERAIS
# =========================

total_livros = len(livros)

total_capitulos = sum(
    len(livro["capitulos"])
    for livro in livros
)

total_leituras = len(leituras)
total_favoritos = len(favoritos)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Livros", total_livros)
col2.metric("Capítulos", total_capitulos)
col3.metric("Leituras", total_leituras)
col4.metric("Favoritos", total_favoritos)

st.divider()


# =========================
# ÚLTIMO CAPÍTULO PUBLICADO
# =========================

st.subheader("🆕 Último capítulo publicado")

capitulos_publicados = []

for livro in livros:
    for indice, capitulo in enumerate(livro.get("capitulos", [])):
        if capitulo.get("status") == "Publicado":
            capitulos_publicados.append(
                {
                    "livro": livro,
                    "indice": indice,
                    "numero": capitulo.get("numero", indice + 1),
                    "titulo": capitulo.get("titulo", "Sem título")
                }
            )

if capitulos_publicados:
    ultimo = capitulos_publicados[-1]
    livro_ultimo = ultimo["livro"]

    with st.container(border=True):
        col_ultimo_1, col_ultimo_2 = st.columns([1, 4])

        with col_ultimo_1:
            capa = livro_ultimo.get("capa", "")

            if imagem_existe(capa):
                st.image(capa, width="stretch")

        with col_ultimo_2:
            st.write(f"📖 **{livro_ultimo['titulo']}**")
            st.caption(
                f"Capítulo {ultimo['numero']} - {ultimo['titulo']}"
            )

            if st.button(
                "Ler capítulo agora",
                key=f"ultimo_capitulo_{livro_ultimo['id']}_{ultimo['numero']}"
            ):
                abrir_capitulo(livro_ultimo, ultimo["indice"])

else:
    st.info("Nenhum capítulo publicado ainda.")

st.divider()


# =========================
# CONTINUAR LENDO
# =========================

st.subheader("📚 Continuar lendo")

leituras_iniciadas = []

for livro in livros:
    livro_id_str = str(livro["id"])

    if livro_id_str in historico_leitura:
        ultimo_capitulo = historico_leitura[livro_id_str]

        if ultimo_capitulo > 0:
            leituras_iniciadas.append(
                {
                    "livro": livro,
                    "ultimo_capitulo": ultimo_capitulo
                }
            )

if leituras_iniciadas:
    for item in leituras_iniciadas[:3]:
        livro = item["livro"]
        ultimo_capitulo = item["ultimo_capitulo"]
        total_capitulos = len(livro["capitulos"])

        progresso = (
            min(ultimo_capitulo / total_capitulos, 1)
            if total_capitulos > 0
            else 0
        )

        with st.container(border=True):
            col_capa, col_info = st.columns([1, 4])

            with col_capa:
                capa = livro.get("capa", "")

                if imagem_existe(capa):
                    st.image(capa, width="stretch")

            with col_info:
                st.write(f"📘 **{livro['titulo']}**")
                st.caption(
                    f"Capítulo {ultimo_capitulo} de {total_capitulos}"
                )

                st.progress(progresso)

                if st.button(
                    "Continuar leitura",
                    key=f"home_continuar_{livro['id']}"
                ):
                    continuar_livro(livro, ultimo_capitulo)

else:
    st.info("Nenhuma leitura iniciada.")

st.divider()


# =========================
# RECOMENDADOS PARA VOCÊ
# =========================

st.subheader("✨ Recomendados para você")

livros_em_leitura_ids = [
    int(livro_id)
    for livro_id in historico_leitura.keys()
]

recomendados = [
    livro
    for livro in livros
    if livro["id"] not in favoritos
    and livro["id"] not in livros_em_leitura_ids
    and livro.get("status") in ["Em publicação", "Finalizado", "Rascunho"]
]

if not recomendados:
    recomendados = [
        livro
        for livro in livros
        if livro["id"] not in favoritos
    ]

if recomendados:
    colunas = st.columns(3)

    for index, livro in enumerate(recomendados[:3]):
        coluna = colunas[index % 3]

        with coluna:
            with st.container(border=True):
                capa = livro.get("capa", "")

                if imagem_existe(capa):
                    st.image(capa, width="stretch")

                st.write(f"📖 **{livro['titulo']}**")
                st.caption(
                    f"{livro.get('categoria', 'Sem categoria')} | {livro.get('status', 'Sem status')}"
                )

                if st.button(
                    "Ver recomendação",
                    key=f"home_recomendado_{livro['id']}"
                ):
                    abrir_livro(livro)

else:
    st.info("Nenhuma recomendação disponível no momento.")

st.divider()


# =========================
# FAVORITOS
# =========================

st.subheader("⭐ Favoritos")

favoritos_lista = [
    livro
    for livro in livros
    if livro["id"] in favoritos
]

if favoritos_lista:
    colunas = st.columns(3)

    for index, livro in enumerate(favoritos_lista[:3]):
        coluna = colunas[index % 3]

        with coluna:
            with st.container(border=True):
                capa = livro.get("capa", "")

                if imagem_existe(capa):
                    st.image(capa, width="stretch")

                st.write(f"⭐ **{livro['titulo']}**")
                st.caption(livro.get("categoria", "Sem categoria"))

                if st.button(
                    "Abrir",
                    key=f"home_favorito_{livro['id']}"
                ):
                    abrir_livro(livro)

else:
    st.info("Nenhum favorito ainda.")

st.divider()


# =========================
# MAIS LIDOS
# =========================

st.subheader("🔥 Mais lidos")

ranking = {}

for leitura in leituras:
    livro_id = leitura.get("livro_id")
    livro_nome = leitura.get("livro", "Livro não identificado")

    if livro_id not in ranking:
        ranking[livro_id] = {
            "nome": livro_nome,
            "total": 0
        }

    ranking[livro_id]["total"] += 1

if ranking:
    ranking_ordenado = sorted(
        ranking.items(),
        key=lambda item: item[1]["total"],
        reverse=True
    )

    for posicao, item in enumerate(
        ranking_ordenado[:5],
        start=1
    ):
        livro_id, dados = item

        livro = next(
            (
                livro
                for livro in livros
                if livro["id"] == livro_id
            ),
            None
        )

        medalha = ""

        if posicao == 1:
            medalha = "🥇"
        elif posicao == 2:
            medalha = "🥈"
        elif posicao == 3:
            medalha = "🥉"

        with st.container(border=True):
            col_rank_1, col_rank_2 = st.columns([1, 4])

            with col_rank_1:
                if livro:
                    capa = livro.get("capa", "")

                    if imagem_existe(capa):
                        st.image(capa, width="stretch")

            with col_rank_2:
                st.write(
                    f"{medalha} **{posicao}º - {dados['nome']}**"
                )
                st.caption(
                    f"{dados['total']} leitura(s) registrada(s)"
                )

                if livro:
                    if st.button(
                        "Ver livro",
                        key=f"home_mais_lido_{livro['id']}"
                    ):
                        abrir_livro(livro)

else:
    st.info("Nenhuma leitura registrada.")

st.divider()


# =========================
# ÚLTIMOS LANÇAMENTOS
# =========================

st.subheader("🆕 Últimos lançamentos")

ultimos_livros = livros[-5:]
ultimos_livros.reverse()

if ultimos_livros:
    for livro in ultimos_livros:
        with st.container(border=True):
            col_livro_1, col_livro_2 = st.columns([1, 4])

            with col_livro_1:
                capa = livro.get("capa", "")

                if imagem_existe(capa):
                    st.image(capa, width="stretch")

            with col_livro_2:
                st.write(f"📖 **{livro['titulo']}**")

                st.caption(
                    f"{livro.get('categoria', 'Sem categoria')} | {livro.get('status', 'Sem status')}"
                )

                st.write(livro.get("descricao", ""))

                if st.button(
                    "Ver livro",
                    key=f"novo_{livro['id']}"
                ):
                    abrir_livro(livro)

else:
    st.info("Nenhum livro cadastrado ainda.")