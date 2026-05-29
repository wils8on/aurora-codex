import streamlit as st

SENHA_AUTOR = "1234"

def verificar_login():

    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if st.session_state["logado"]:

        with st.sidebar:

            st.success("Autor autenticado")

            if st.button("Logout"):

                st.session_state["logado"] = False
                st.rerun()

        return True

    st.title("🔐 Acesso restrito")

    senha = st.text_input(
        "Digite a senha do autor",
        type="password"
    )

    if st.button("Entrar"):

        if senha == SENHA_AUTOR:

            st.session_state["logado"] = True

            st.success("Login realizado com sucesso.")

            st.rerun()

        else:

            st.error("Senha incorreta.")

    return False
    