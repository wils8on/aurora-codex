from utils import carregar_leitor, salvar_leitor

import streamlit as st
import json
import math
from pathlib import Path

st.title("🌌 Livro")

CAMINHO_LIVROS = "data/livros.json"
PALAVRAS_POR_MINUTO = 200


def contar_palavras(texto):
    return len(texto.split())


def formatar_numero(numero):
    return f"{numero:,}".replace(",", ".")


def formatar_tempo(minutos_totais):
    if minutos_totais <= 0:
        return "0min"

    horas = minutos_totais // 60
    minutos = minutos_totais % 60

    if horas > 0:
        return f"{horas}h {minutos:02d}min"

    return f"{minutos}min"


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
        dados_leitor = carregar_leitor()

        favoritos = dados_leitor["favoritos"]
        historico_leitura = dados_leitor["historico_leitura"]

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

            favoritado = livro["id"] in favoritos

            if favoritado:
                if st.button("⭐ Favoritado"):
                    favoritos.remove(livro["id"])
                    dados_leitor["favoritos"] = favoritos
                    salvar_leitor(dados_leitor)
                    st.rerun()
            else:
                if st.button("☆ Favoritar"):
                    favoritos.append(livro["id"])
                    dados_leitor["favoritos"] = favoritos
                    salvar_leitor(dados_leitor)
                    st.rerun()

            st.caption(
                f"Autor: {livro['autor']} | Status: {livro['status']} | Categoria: {livro.get('categoria', 'Sem categoria')}"
            )

            st.write(livro["descricao"])

            st.divider()

            total_capitulos = len(livro["capitulos"])
            livro_id_str = str(livro_id)

            total_palavras = sum(
                contar_palavras(
                    capitulo.get("conteudo", "")
                )
                for capitulo in livro["capitulos"]
            )

            tempo_total_minutos = math.ceil(
                total_palavras / PALAVRAS_POR_MINUTO
            ) if total_palavras > 0 else 0

            if total_capitulos > 0:
                media_palavras = int(
                    total_palavras / total_capitulos
                )
            else:
                media_palavras = 0

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

            col_metricas_1, col_metricas_2 = st.columns(2)

            with col_metricas_1:
                st.metric(
                    "Capítulos",
                    total_capitulos
                )

                st.metric(
                    "Palavras",
                    formatar_numero(total_palavras)
                )

            with col_metricas_2:
                st.metric(
                    "Tempo estimado",
                    formatar_tempo(tempo_total_minutos)
                )

                st.metric(
                    "Média por capítulo",
                    formatar_numero(media_palavras)
                )

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
                palavras_capitulo = contar_palavras(
                    capitulo.get("conteudo", "")
                )

                tempo_capitulo = math.ceil(
                    palavras_capitulo / PALAVRAS_POR_MINUTO
                ) if palavras_capitulo > 0 else 0

                with st.container(border=True):
                    st.write(
                        f"Capítulo {capitulo['numero']} - {capitulo['titulo']}"
                    )
                    st.caption(
                        f"Status: {capitulo['status']} | {formatar_numero(palavras_capitulo)} palavras | {formatar_tempo(tempo_capitulo)} de leitura"
                    )
        else:
            st.info("Nenhum capítulo cadastrado ainda.")