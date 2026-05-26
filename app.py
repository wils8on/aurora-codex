import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Aurora Codex",
    page_icon="📚",
    layout="wide"
)

# Título principal
st.title("📚 Aurora Codex")

# Subtítulo
st.subheader("Sua plataforma de leitura imersiva")

# Texto principal
st.write("""
Bem-vindo ao Aurora Codex.

Aqui você poderá:

- organizar livros;
- publicar capítulos;
- criar personagens;
- construir universos narrativos;
- adicionar trilhas sonoras;
- desenvolver experiências imersivas.
""")

# Caixa de destaque
st.info("Primeira versão do projeto em desenvolvimento.")