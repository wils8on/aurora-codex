import json
from pathlib import Path

CAMINHO_LEITOR = "data/leitor.json"


def carregar_leitor():

    if not Path(CAMINHO_LEITOR).exists():

        dados = {
            "favoritos": [],
            "historico_leitura": {}
        }

        with open(
            CAMINHO_LEITOR,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                dados,
                file,
                indent=4,
                ensure_ascii=False
            )

    with open(
        CAMINHO_LEITOR,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def salvar_leitor(dados):

    with open(
        CAMINHO_LEITOR,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dados,
            file,
            indent=4,
            ensure_ascii=False
        )