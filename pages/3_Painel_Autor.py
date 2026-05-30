from datetime import datetime
from pathlib import Path
import streamlit as st
import json
import re
import math

from auth import verificar_login

if not verificar_login():
    st.stop()

st.title("✍️ Painel do Autor")

CAMINHO_LIVROS = "data/livros.json"
CAMINHO_HISTORICO = "data/historico.json"
CAMINHO_LEITURAS = "data/leituras.json"
PASTA_CAPAS = "assets/capas"
PASTA_BANNERS = "assets/banners"
PALAVRAS_POR_MINUTO = 200

Path(PASTA_CAPAS).mkdir(parents=True, exist_ok=True)
Path(PASTA_BANNERS).mkdir(parents=True, exist_ok=True)


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


def carregar_leituras():
    try:
        with open(CAMINHO_LEITURAS, "r", encoding="utf-8") as file:
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


def gerar_nome_arquivo(texto):
    nome = texto.lower().strip()
    nome = re.sub(r"[^a-z0-9áàâãéèêíïóôõöúçñ\s_-]", "", nome)
    nome = re.sub(r"\s+", "_", nome)
    return nome


def salvar_upload_capa(upload_capa, titulo_livro):
    if upload_capa is None:
        return ""

    nome_base = gerar_nome_arquivo(titulo_livro)
    extensao = upload_capa.name.split(".")[-1].lower()
    caminho_capa = f"{PASTA_CAPAS}/{nome_base}.{extensao}"

    with open(caminho_capa, "wb") as arquivo:
        arquivo.write(upload_capa.getbuffer())

    return caminho_capa


def salvar_upload_banner(upload_banner, titulo_livro):
    if upload_banner is None:
        return ""

    nome_base = gerar_nome_arquivo(titulo_livro)
    extensao = upload_banner.name.split(".")[-1].lower()
    caminho_banner = f"{PASTA_BANNERS}/{nome_base}.{extensao}"

    with open(caminho_banner, "wb") as arquivo:
        arquivo.write(upload_banner.getbuffer())

    return caminho_banner


def contar_palavras(texto):
    return len(texto.split())


def contar_palavras_livro(livro):
    return sum(
        contar_palavras(capitulo.get("conteudo", ""))
        for capitulo in livro.get("capitulos", [])
    )


def calcular_tempo_minutos(total_palavras):
    if total_palavras <= 0:
        return 0

    return max(1, math.ceil(total_palavras / PALAVRAS_POR_MINUTO))


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


livros = carregar_livros()

if st.session_state.get("ir_para_dashboard"):
    st.session_state["opcao_painel"] = "📊 Dashboard"
    del st.session_state["ir_para_dashboard"]

opcao_painel = st.radio(
    "Menu do Painel",
    [
        "📊 Dashboard",
        "📘 Cadastrar Livro",
        "✏️ Editar Livro",
        "🗑️ Excluir Livro",
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

    leituras = carregar_leituras()
    total_leituras = len(leituras)

    ranking_leituras = {}

    for leitura in leituras:
        livro_nome = leitura.get("livro", "Livro não identificado")
        ranking_leituras[livro_nome] = ranking_leituras.get(livro_nome, 0) + 1

    livro_mais_lido = "-"

    if ranking_leituras:
        livro_mais_lido = max(
            ranking_leituras,
            key=ranking_leituras.get
        )

    total_livros = len(livros)

    total_capitulos = sum(
        len(livro["capitulos"]) for livro in livros
    )

    capitulos_publicados = sum(
        1
        for livro in livros
        for capitulo in livro["capitulos"]
        if capitulo["status"] == "Publicado"
    )

    total_palavras = sum(
        contar_palavras_livro(livro)
        for livro in livros
    )

    tempo_total_minutos = calcular_tempo_minutos(total_palavras)

    maior_obra = None

    if livros:
        maior_obra = max(
            livros,
            key=lambda livro: contar_palavras_livro(livro)
        )

    col1, col2, col3 = st.columns(3)

    col1.metric("Livros", total_livros)
    col2.metric("Capítulos", total_capitulos)
    col3.metric("Publicados", capitulos_publicados)

    col4, col5, col6 = st.columns(3)

    col4.metric("Palavras totais", formatar_numero(total_palavras))
    col5.metric("Tempo total estimado", formatar_tempo(tempo_total_minutos))
    col6.metric("Maior obra", maior_obra["titulo"] if maior_obra else "-")

    col7, col8, col9 = st.columns(3)

    col7.metric("Leituras registradas", total_leituras)
    col8.metric("Livro mais lido", livro_mais_lido)
    col9.metric("Capítulos lidos", total_leituras)

    st.divider()

    st.subheader("🏆 Ranking de Leituras")

    if ranking_leituras:
        ranking_ordenado = sorted(
            ranking_leituras.items(),
            key=lambda item: item[1],
            reverse=True
        )

        for posicao, item in enumerate(ranking_ordenado, start=1):
            livro_nome, total = item

            medalha = ""

            if posicao == 1:
                medalha = "🥇"
            elif posicao == 2:
                medalha = "🥈"
            elif posicao == 3:
                medalha = "🥉"

            with st.container(border=True):
                st.write(
                    f"{medalha} **{posicao}º - {livro_nome}**"
                )
                st.caption(
                    f"{total} leitura(s) registrada(s)"
                )

    else:
        st.info("Nenhuma leitura registrada ainda.")

    st.divider()

    st.subheader("Obras cadastradas")

    for livro in livros:
        palavras_livro = contar_palavras_livro(livro)
        tempo_livro = calcular_tempo_minutos(palavras_livro)
        total_capitulos_livro = len(livro["capitulos"])

        leituras_livro = len(
            [
                leitura
                for leitura in leituras
                if leitura.get("livro_id") == livro["id"]
            ]
        )

        if total_capitulos_livro > 0:
            media_palavras = int(
                palavras_livro / total_capitulos_livro
            )
        else:
            media_palavras = 0

        with st.container(border=True):
            st.write(f"📘 **{livro['titulo']}**")
            st.caption(
                f"Status: {livro['status']} | Categoria: {livro.get('categoria', 'Sem categoria')} | Capítulos: {total_capitulos_livro}"
            )
            st.caption(
                f"Palavras: {formatar_numero(palavras_livro)} | Tempo estimado: {formatar_tempo(tempo_livro)} | Média por capítulo: {formatar_numero(media_palavras)} | Leituras: {leituras_livro}"
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

        categoria_livro = st.selectbox(
            "Categoria",
            [
                "Romance",
                "Distopia",
                "Fantasia",
                "Sci-Fi",
                "Drama",
                "Terror",
                "Suspense",
                "Aventura",
                "Outro"
            ]
        )

        descricao_livro = st.text_area(
            "Descrição do livro",
            height=150
        )

        upload_capa = st.file_uploader(
            "Capa do livro",
            type=["png", "jpg", "jpeg"],
            key="upload_capa_livro"
        )

        upload_banner = st.file_uploader(
            "Banner do livro",
            type=["png", "jpg", "jpeg"],
            key="upload_banner_livro"
        )

        if st.button("Salvar livro"):
            if not titulo_livro or not descricao_livro:
                st.warning("Preencha o título e a descrição do livro.")
            else:
                novo_id = max([livro["id"] for livro in livros], default=0) + 1

                caminho_capa = salvar_upload_capa(
                    upload_capa,
                    titulo_livro
                )

                caminho_banner = salvar_upload_banner(
                    upload_banner,
                    titulo_livro
                )

                novo_livro = {
                    "id": novo_id,
                    "titulo": titulo_livro,
                    "autor": autor_livro,
                    "status": status_livro,
                    "categoria": categoria_livro,
                    "descricao": descricao_livro,
                    "capa": caminho_capa,
                    "banner": caminho_banner,
                    "capitulos": []
                }

                livros.append(novo_livro)
                salvar_livros(livros)

                registrar_historico(
                    "Cadastro de livro",
                    titulo_livro,
                    "-",
                    f"Livro criado com status: {status_livro}, categoria: {categoria_livro}, capa: {caminho_capa or 'não enviada'} e banner: {caminho_banner or 'não enviado'}."
                )

                voltar_dashboard(
                    f"Livro '{titulo_livro}' cadastrado com sucesso."
                )


elif opcao_painel == "✏️ Editar Livro":
    st.subheader("Editar livro")

    if not livros:
        st.warning("Nenhum livro cadastrado.")
    else:
        livro_edicao = st.selectbox(
            "Escolha o livro para edição",
            livros,
            format_func=lambda livro: livro["titulo"],
            key="editar_livro"
        )

        categorias = [
            "Romance",
            "Distopia",
            "Fantasia",
            "Sci-Fi",
            "Drama",
            "Terror",
            "Suspense",
            "Aventura",
            "Outro"
        ]

        categoria_atual = livro_edicao.get("categoria", "Outro")

        if categoria_atual not in categorias:
            categoria_atual = "Outro"

        with st.container(border=True):
            novo_titulo = st.text_input(
                "Título do livro",
                value=livro_edicao["titulo"]
            )

            novo_autor = st.text_input(
                "Autor",
                value=livro_edicao["autor"]
            )

            novo_status = st.selectbox(
                "Status",
                ["Rascunho", "Em publicação", "Finalizado"],
                index=["Rascunho", "Em publicação", "Finalizado"].index(
                    livro_edicao.get("status", "Rascunho")
                )
            )

            nova_categoria = st.selectbox(
                "Categoria",
                categorias,
                index=categorias.index(categoria_atual)
            )

            nova_descricao = st.text_area(
                "Descrição do livro",
                value=livro_edicao["descricao"],
                height=150
            )

            capa_atual = livro_edicao.get("capa", "")

            if capa_atual:
                st.caption(f"Capa atual: {capa_atual}")

            nova_capa_manual = st.text_input(
                "Caminho da capa",
                value=capa_atual
            )

            upload_nova_capa = st.file_uploader(
                "Enviar nova capa",
                type=["png", "jpg", "jpeg"],
                key=f"upload_capa_edicao_{livro_edicao['id']}"
            )

            banner_atual = livro_edicao.get("banner", "")

            if banner_atual:
                st.caption(f"Banner atual: {banner_atual}")

            novo_banner_manual = st.text_input(
                "Caminho do banner",
                value=banner_atual
            )

            upload_novo_banner = st.file_uploader(
                "Enviar novo banner",
                type=["png", "jpg", "jpeg"],
                key=f"upload_banner_edicao_{livro_edicao['id']}"
            )

            if st.button("Salvar alterações do livro"):
                if not novo_titulo or not nova_descricao:
                    st.warning("Preencha o título e a descrição do livro.")
                else:
                    alteracoes = []

                    caminho_capa_final = nova_capa_manual

                    if upload_nova_capa is not None:
                        caminho_capa_final = salvar_upload_capa(
                            upload_nova_capa,
                            novo_titulo
                        )

                    caminho_banner_final = novo_banner_manual

                    if upload_novo_banner is not None:
                        caminho_banner_final = salvar_upload_banner(
                            upload_novo_banner,
                            novo_titulo
                        )

                    if novo_titulo != livro_edicao["titulo"]:
                        alteracoes.append(
                            f"Título alterado de '{livro_edicao['titulo']}' para '{novo_titulo}'"
                        )

                    if novo_autor != livro_edicao["autor"]:
                        alteracoes.append(
                            f"Autor alterado de '{livro_edicao['autor']}' para '{novo_autor}'"
                        )

                    if novo_status != livro_edicao["status"]:
                        alteracoes.append(
                            f"Status alterado de '{livro_edicao['status']}' para '{novo_status}'"
                        )

                    if nova_categoria != livro_edicao.get("categoria", "Sem categoria"):
                        alteracoes.append(
                            f"Categoria alterada para '{nova_categoria}'"
                        )

                    if nova_descricao != livro_edicao["descricao"]:
                        alteracoes.append("Descrição do livro atualizada")

                    if caminho_capa_final != livro_edicao.get("capa", ""):
                        alteracoes.append("Capa atualizada")

                    if caminho_banner_final != livro_edicao.get("banner", ""):
                        alteracoes.append("Banner atualizado")

                    if not alteracoes:
                        alteracoes.append("Nenhuma alteração relevante identificada")

                    titulo_original = livro_edicao["titulo"]

                    for livro in livros:
                        if livro["id"] == livro_edicao["id"]:
                            livro["titulo"] = novo_titulo
                            livro["autor"] = novo_autor
                            livro["status"] = novo_status
                            livro["categoria"] = nova_categoria
                            livro["descricao"] = nova_descricao
                            livro["capa"] = caminho_capa_final
                            livro["banner"] = caminho_banner_final

                    salvar_livros(livros)

                    registrar_historico(
                        "Edição de livro",
                        titulo_original,
                        "-",
                        " | ".join(alteracoes)
                    )

                    voltar_dashboard(
                        f"Livro '{novo_titulo}' atualizado com sucesso."
                    )


elif opcao_painel == "🗑️ Excluir Livro":
    st.subheader("Excluir livro")

    if not livros:
        st.warning("Nenhum livro cadastrado.")
    else:
        livro_exclusao = st.selectbox(
            "Escolha o livro para excluir",
            livros,
            format_func=lambda livro: livro["titulo"],
            key="livro_excluir"
        )

        st.error(
            f"Você está prestes a excluir o livro '{livro_exclusao['titulo']}' "
            f"e todos os seus {len(livro_exclusao['capitulos'])} capítulos."
        )

        confirmar = st.checkbox(
            "Confirmo que desejo excluir este livro."
        )

        if st.button("Excluir livro"):
            if not confirmar:
                st.warning("Marque a confirmação antes de excluir.")
            else:
                titulo_excluido = livro_exclusao["titulo"]
                livro_id_excluido = livro_exclusao["id"]

                livros = [
                    livro
                    for livro in livros
                    if livro["id"] != livro_id_excluido
                ]

                salvar_livros(livros)

                registrar_historico(
                    "Exclusão de livro",
                    titulo_excluido,
                    "-",
                    "Livro removido juntamente com todos os capítulos."
                )

                voltar_dashboard(
                    f"Livro '{titulo_excluido}' excluído com sucesso."
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