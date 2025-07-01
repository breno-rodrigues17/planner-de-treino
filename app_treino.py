import streamlit as st
import json
import os
import pandas as pd
from datetime import date, datetime
import shutil

# ARQUIVOS
ARQUIVO_TREINOS = "treinos.json"
ARQUIVO_REGISTRO = "registro_treinos.json"
ARQUIVO_VIDEOS = "videos.json"
PASTA_VIDEOS = "videos"

# Funções auxiliares
def carregar_json(caminho, padrao):
    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            return json.load(f)
    return padrao

def salvar_json(caminho, dados):
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4)

os.makedirs(PASTA_VIDEOS, exist_ok=True)

# Carregamento de dados
treinos = carregar_json(ARQUIVO_TREINOS, {dia: [] for dia in ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]})
registros = carregar_json(ARQUIVO_REGISTRO, [])
videos = carregar_json(ARQUIVO_VIDEOS, [])

# UI
st.title("🏋️ Planner de Treino")

dia = st.selectbox("Escolha o dia da semana", list(treinos.keys()))
st.subheader(f"📅 Treinos de {dia.capitalize()}")

if treinos[dia]:
    for i, treino in enumerate(treinos[dia]):
        st.markdown(f"**{i+1}. {treino['exercicio']}** – {treino['series']}")
        if treino["video"]:
            st.video(treino["video"])
else:
    st.info("Nenhum treino cadastrado para esse dia.")

st.divider()
st.subheader("➕ Adicionar novo exercício")

with st.form("form_treino"):
    nome_exercicio = st.text_input("Nome do exercício")
    series = st.text_input("Séries e repetições (ex: 4x12)")
    link_video = st.text_input("Link do vídeo (YouTube)", placeholder="https://...")
    enviar = st.form_submit_button("Salvar")

    if enviar and nome_exercicio and series:
        treinos[dia].append({
            "exercicio": nome_exercicio,
            "series": series,
            "video": link_video
        })
        salvar_json(ARQUIVO_TREINOS, treinos)
        st.success(f"✅ {nome_exercicio} adicionado ao treino de {dia.capitalize()}!")
        st.experimental_rerun()

# Registro de treino
st.divider()
st.subheader("✅ Registrar treino feito")

for i, treino in enumerate(treinos[dia]):
    with st.expander(f"{treino['exercicio']} – {treino['series']}"):
        st.video(treino["video"])
        peso_usado = st.text_input(f"Peso usado no exercício {i+1}", key=f"peso_{i}")
        observacao = st.text_area(f"Observações (opcional)", key=f"obs_{i}")
        if st.button(f"💾 Registrar treino {i+1}", key=f"btn_{i}"):
            novo_registro = {
                "data": str(date.today()),
                "dia": dia,
                "exercicio": treino["exercicio"],
                "peso_usado": peso_usado,
                "observacao": observacao
            }
            registros.append(novo_registro)
            salvar_json(ARQUIVO_REGISTRO, registros)
            st.success(f"Treino de {treino['exercicio']} registrado com sucesso!")

# Histórico
st.divider()
st.subheader("📖 Histórico de Treinos")

if registros:
    df = pd.DataFrame(registros)
    st.dataframe(df)
else:
    st.info("Nenhum treino registrado ainda.")

# Upload de vídeo
st.divider()
st.subheader("📤 Enviar vídeo do treino")

video_file = st.file_uploader("Escolha um vídeo (MP4)", type=["mp4", "mov", "avi"])
descricao_video = st.text_input("Descrição do vídeo (ex: Agachamento 4x10)")
enviar_video = st.button("🚀 Enviar vídeo")

if enviar_video and video_file and descricao_video:
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{data_hora}_{video_file.name}"
    caminho_salvo = os.path.join(PASTA_VIDEOS, nome_arquivo)

    with open(caminho_salvo, "wb") as f:
        shutil.copyfileobj(video_file, f)

    videos.append({
        "arquivo": nome_arquivo,
        "descricao": descricao_video,
        "data": str(date.today())
    })
    salvar_json(ARQUIVO_VIDEOS, videos)

    st.success("✅ Vídeo enviado com sucesso!")
    st.experimental_rerun()

# Visualização dos vídeos enviados
st.subheader("🎥 Vídeos enviados")

if videos:
    for video in reversed(videos):
        st.markdown(f"**{video['descricao']}** – 📅 {video['data']}")
        caminho_video = os.path.join(PASTA_VIDEOS, video["arquivo"])
        st.video(caminho_video)
else:
    st.info("Nenhum vídeo enviado ainda.")
