from utils import carregar_leitor, salvar_leitor

from datetime import datetime
from pathlib import Path
import streamlit as st
import json
import math

st.title("📚 Leitura")

CAMINHO_LIVROS = "data/livros.json"
CAMINHO_LEITURAS = "data/leituras.json"
PALAVRAS_POR_MINUTO = 200


def contar_palavras(texto):
    return len(texto.split())


def calcular_tempo_leitura(texto):
    total_palavras = contar_palavras(texto)

    if total_palavras == 0:
        return 0

    return max(
        1,
        math.ceil(total_palavras / PALAVRAS_POR_MINUTO)
    )


def carregar_leituras():
    if not Path(CAMINHO_LEITURAS).exists():
        with open(CAMINHO_LEITURAS, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)

    with open(CAMINHO_LEITURAS, "r", encoding="utf-8") as file:
        return json.load(file)


def salvar_leituras(leituras):
    with open(CAMINHO_LEITURAS, "w", encoding="utf-8") as file:
        json.dump(leituras, file, ensure_ascii=False, indent=4)


def registrar_leitura(livro, capitulo):
    leituras = carregar_leituras()

    novo_registro = {
        "livro_id": livro["id"],
        "livro": livro["titulo"],
        "capitulo": capitulo["numero"],
        "titulo_capitulo": capitulo["titulo"],
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    leituras.insert(0, novo_registro)

    salvar_leituras(leituras)


with open(CAMINHO_LIVROS, "r", encoding="utf-8") as file:
    livros = json.load(file)

livro_id = st.session_state.get("livro_selecionado")

if livro_id is None:
    st.warning("Nenhum livro selecionado.")

else:
    livro = next(
        (l for l in livros if l["id"] == livro_id),
        None
    )

    if livro is None:
        st.error("Livro não encontrado.")

    else:
        st.header(livro["titulo"])

        capitulos = livro["capitulos"]

        if not capitulos:
            st.warning("Este livro ainda não possui capítulos.")

        else:
            dados_leitor = carregar_leitor()

            historico_leitura = dados_leitor["historico_leitura"]

            livro_id_str = str(livro_id)

            capitulo_index = st.session_state.get("capitulo_index", 0)

            if capitulo_index >= len(capitulos):
                capitulo_index = 0

            capitulo = st.selectbox(
                "Escolha o capítulo",
                capitulos,
                index=capitulo_index,
                format_func=lambda c: f"Capítulo {c['numero']} - {c['titulo']}"
            )

            indice_atual = capitulos.index(capitulo)
            total_capitulos = len(capitulos)

            conteudo_capitulo = capitulo.get("conteudo", "")
            total_palavras = contar_palavras(conteudo_capitulo)
            tempo_leitura = calcular_tempo_leitura(conteudo_capitulo)

            st.divider()

            col1, col2 = st.columns([4, 1])

            with col1:
                st.subheader(capitulo["titulo"])
                st.caption(
                    f"{total_palavras} palavras | {tempo_leitura} min de leitura"
                )

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
                    {conteudo_capitulo}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("")

            if st.button("✅ Marcar como concluído"):
                historico_leitura[livro_id_str] = capitulo["numero"]

                dados_leitor["historico_leitura"] = historico_leitura

                salvar_leitor(dados_leitor)

                registrar_leitura(
                    livro,
                    capitulo
                )

                st.success(
                    f"Capítulo {capitulo['numero']} marcado como concluído e leitura registrada."
                )

            st.divider()

            col_anterior, col_centro, col_proximo = st.columns([1, 1, 1])

            with col_anterior:
                if indice_atual > 0:
                    if st.button("⬅️ Capítulo anterior"):
                        st.session_state["capitulo_index"] = indice_atual - 1
                        st.rerun()

            with col_centro:
                st.markdown(
                    f"<div style='text-align:center;'>Capítulo {indice_atual + 1} de {total_capitulos}</div>",
                    unsafe_allow_html=True
                )

            with col_proximo:
                if indice_atual < total_capitulos - 1:
                    if st.button("Próximo capítulo ➡️"):
                        st.session_state["capitulo_index"] = indice_atual + 1
                        st.rerun()