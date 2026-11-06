import base64
import csv
from datetime import datetime
import io
import os
from openai import OpenAI
import pandas as pd
import plotly.express as px
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Corretor Automático de Provas com IA",
    page_icon="📝",
    layout="wide",
)

ARQUIVO_CSV = "historico_correcoes.csv"


# --- ESQUEMA PYDANTIC PARA STRUCTURED OUTPUTS ---
class CorrecaoProva(BaseModel):
  nota_atribuida: float = Field(description="Nota final atribuída ao aluno.")
  nota_maxima: float = Field(description="Nota máxima possível da prova.")
  pontos_fortes: list[str] = Field(description="Acertos ou raciocínios corretos.")
  erros_cometidos: list[str] = Field(
      description="Erros conceituais ou de cálculo."
  )
  feedback_construtivo: str = Field(description="Feedback pedagógico detalhado.")


# --- FUNÇÕES DE GERAÇÃO DE RELATÓRIOS PDF (REPORTLAB) ---
def gerar_pdf_relatorio(nome_aluno, correcao):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=54,
      leftMargin=54,
      topMargin=54,
      bottomMargin=54,
  )
  elementos = []
  styles = getSampleStyleSheet()

  estilo_titulo = ParagraphStyle(
      "TituloRelatorio",
      parent=styles["Heading1"],
      fontSize=18,
      textColor=colors.HexColor("#1F2937"),
      spaceAfter=15,
      alignment=1,
  )
  estilo_subtitulo = ParagraphStyle(
      "SubTitulo",
      parent=styles["Heading2"],
      fontSize=12,
      textColor=colors.HexColor("#4B5563"),
      spaceAfter=10,
  )
  estilo_corpo = ParagraphStyle(
      "CorpoTexto",
      parent=styles["Normal"],
      fontSize=10,
      textColor=colors.HexColor("#374151"),
      spaceAfter=6,
  )

  elementos.append(
      Paragraph("RELATÓRIO DE AVALIAÇÃO DA APRENDIZAGEM", estilo_titulo)
  )
  elementos.append(Spacer(1, 10))

  dados_cabecalho = [[
      Paragraph(f"<b>Aluno(a):</b> {nome_aluno}", estilo_corpo),
      Paragraph(
          f"<b>Nota Final:</b> {correcao.nota_atribuida} /"
          f" {correcao.nota_maxima}",
          estilo_corpo,
      ),
  ]]
  tabela_cabecalho = Table(dados_cabecalho, colWidths=[300, 204])
  tabela_cabecalho.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F4F6")),
          ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("PADDING", (0, 0), (-1, -1), 8),
      ])
  )
  elementos.append(tabela_cabecalho)
  elementos.append(Spacer(1, 20))

  elementos.append(Paragraph("✅ Pontos Fortes e Acertos", estilo_subtitulo))
  for ponto in correcao.pontos_fortes:
    elementos.append(Paragraph(f"• {ponto}", estilo_corpo))
  elementos.append(Spacer(1, 15))

  elementos.append(Paragraph("❌ Pontos de Atenção e Erros", estilo_subtitulo))
  for erro in correcao.erros_cometidos:
    elementos.append(Paragraph(f"• {erro}", estilo_corpo))
  elementos.append(Spacer(1, 15))

  elementos.append(Paragraph("💡 Feedback Pedagógico Detalhado", estilo_subtitulo))
  elementos.append(Paragraph(correcao.feedback_construtivo, estilo_corpo))

  doc.build(elementos)
  buffer.seek(0)
  return buffer


def gerar_pdf_consolidado_turma(caminho_csv):
  if not os.path.exists(caminho_csv):
    return None
  df = pd.read_csv(caminho_csv)
  if df.empty:
    return None

  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=36,
      leftMargin=36,
      topMargin=36,
      bottomMargin=36,
  )
  elementos = []
  styles = getSampleStyleSheet()

  estilo_titulo = ParagraphStyle(
      "TituloConsolidado",
      parent=styles["Heading1"],
      fontSize=16,
      textColor=colors.HexColor("#0F172A"),
      spaceAfter=6,
  )
  estilo_subtitulo = ParagraphStyle(
      "SubTituloConsolidado",
      parent=styles["Heading2"],
      fontSize=12,
      textColor=colors.HexColor("#1E293B"),
      spaceAfter=8,
      spaceBefore=12,
  )
  estilo_texto = ParagraphStyle(
      "CorpoTexto",
      parent=styles["Normal"],
      fontSize=9,
      textColor=colors.HexColor("#334155"),
  )
  estilo_th = ParagraphStyle(
      "HeaderTabela",
      parent=styles["Normal"],
      fontSize=9.5,
      fontName="Helvetica-Bold",
      textColor=colors.white,
  )

  elementos.append(Paragraph("RELATÓRIO CONSOLIDADO DA TURMA", estilo_titulo))
  elementos.append(
      Paragraph(
          "<b>Sistema de Correção de Provas Manuscritas via IA</b>", estilo_texto
      )
  )
  elementos.append(Spacer(1, 12))

  total_provas = len(df)
  media_turma = df["Nota_Atribuida"].mean()
  maior_nota = df["Nota_Atribuida"].max()
  menor_nota = df["Nota_Atribuida"].min()

  dados_kpi = [
      [
          Paragraph("<b>TOTAL PROVAS</b>", estilo_texto),
          Paragraph("<b>MÉDIA TURMA</b>", estilo_texto),
          Paragraph("<b>MAIOR NOTA</b>", estilo_texto),
          Paragraph("<b>MENOR NOTA</b>", estilo_texto),
      ],
      [
          Paragraph(f"<b>{total_provas}</b>", estilo_titulo),
          Paragraph(f"<b>{media_turma:.1f}</b>", estilo_titulo),
          Paragraph(f"<b>{maior_nota:.1f}</b>", estilo_titulo),
          Paragraph(f"<b>{menor_nota:.1f}</b>", estilo_titulo),
      ],
  ]
  tabela_kpi = Table(dados_kpi, colWidths=[135, 135, 135, 135])
  tabela_kpi.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
          ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("PADDING", (0, 0), (-1, -1), 6),
      ])
  )
  elementos.append(tabela_kpi)
  elementos.append(Spacer(1, 14))

  elementos.append(
      Paragraph("Detalhamento por Aluno e Desempenho", estilo_subtitulo)
  )
  dados_tabela = [[
      Paragraph("Aluno", estilo_th),
      Paragraph("Data/Hora", estilo_th),
      Paragraph("Nota", estilo_th),
      Paragraph("Feedback Construtivo Sintético", estilo_th),
  ]]

  for _, row in df.iterrows():
    feedback_curto = (
        (str(row["Feedback"])[:120] + "...")
        if len(str(row["Feedback"])) > 120
        else str(row["Feedback"])
    )
    dados_tabela.append([
        Paragraph(f"<b>{row['Aluno']}</b>", estilo_texto),
        Paragraph(str(row["Data_Hora"]), estilo_texto),
        Paragraph(
            f"<b>{row['Nota_Atribuida']:.1f} / {row['Nota_Maxima']:.1f}</b>",
            estilo_texto,
        ),
        Paragraph(feedback_curto, estilo_texto),
    ])

  tabela_alunos = Table(
      dados_tabela, colWidths=[110, 85, 75, 270], repeatRows=1
  )
  tabela_alunos.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#F8FAFC")],
          ),
          ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
          ("PADDING", (0, 0), (-1, -1), 6),
      ])
  )
  elementos.append(tabela_alunos)

  doc.build(elementos)
  buffer.seek(0)
  return buffer


# --- INTERFACE STREAMLIT ---
st.title("🤖 Corretor de Provas Manuscritas com IA - 06/11/2026")
st.markdown(
    "Faça o upload da imagem da prova, configure o gabarito dinâmico e obtenha"
    " correções instantâneas, relatórios em PDF e estatísticas da turma."
)

# --- BARRA LATERAL: CONFIGURAÇÕES E GABARITO DINÂMICO ---
with st.sidebar:
  st.header("⚙️ Configurações")
#  api_key = st.text_input(
#      "Chave da API OpenAI",
#      type="password",
#      placeholder="sk-...",
#      help="Insira sua chave de API da OpenAI.",
#  )
  # Em vez de st.text_input para a chave, você pode carregar direto dos secrets:
  api_key = st.secrets.get("OPENAI_API_KEY", "")
  if not api_key:
      api_key = st.sidebar.text_input("Chave da API OpenAI", type="password")

  st.markdown("---")
  st.subheader("📋 Critérios e Pesos da Prova")

  dados_iniciais = pd.DataFrame({
      "Questao": ["Questão 1", "Questão 2"],
      "Descricao": [
          "Calcular a derivada de f(x) = x^3 (Resposta esperada: 3x^2)",
          (
              "Calcular o limite fundamental sen(x)/x com x->0 (Resposta"
              " esperada: 1)"
          ),
      ],
      "Valor": [5.0, 5.0],
  })

  tabela_editada = st.data_editor(
      dados_iniciais,
      num_rows="dynamic",
      column_config={
          "Questao": st.column_config.TextColumn(
              "Nome/Número", required=True, max_chars=30
          ),
          "Descricao": st.column_config.TextColumn(
              "Gabarito e Critérios", required=True, width="large"
          ),
          "Valor": st.column_config.NumberColumn(
              "Pontos", min_value=0.0, max_value=100.0, step=0.5, format="%.1f"
          ),
      },
      width="stretch",
      key="editor_gabarito",
  )

  nota_maxima_total = tabela_editada["Valor"].sum()
  st.info(f"🏆 **Nota Máxima Total:** {nota_maxima_total:.1f} pontos")

  gabarito_e_rubrica = f"Nota Máxima Total: {nota_maxima_total}\nCritérios:\n"
  for _, row in tabela_editada.iterrows():
    gabarito_e_rubrica += (
        f"- {row['Questao']} (Valor: {row['Valor']} pontos): {row['Descricao']}\n"
    )

# --- ÁREA PRINCIPAL: UPLOAD E CORREÇÃO ---
arquivo_enviado = st.file_uploader(
    "Envie a imagem da prova manuscrita do aluno", type=["jpg", "jpeg", "png"]
)
nome_aluno = st.text_input(
    "Nome do Aluno(a):", value="Estudante Exemplo", max_chars=100
)

if arquivo_enviado is not None:
  st.image(
      arquivo_enviado,
      caption="Prova Manuscrita do Aluno",
      width="stretch",
  )

  if st.button("✨ Executar Correção Inteligente", type="primary"):
    if not api_key:
      st.error(
          "Por favor, informe sua chave da API da OpenAI na barra lateral."
      )
    else:
      with st.spinner("Analisando caligrafia e avaliando com GPT-4o..."):
        try:
          client = OpenAI(api_key=api_key)
          bytes_imagem = arquivo_enviado.getvalue()
          imagem_base64 = base64.b64encode(bytes_imagem).decode("utf-8")

          prompt_sistema = (
              "Você é um professor assistente especialista em pedagogia e"
              " exatas. Analise imagens de provas manuscritas aplicando"
              " rigorosamente a rubrica fornecida. A nota máxima deve ser"
              f" exatamente {nota_maxima_total}."
          )
          prompt_usuario = (
              f"Gabarito e rubrica:\n{gabarito_e_rubrica}\n\nAnalise a imagem"
              " manuscrita da prova do aluno anexa e preencha a avaliação"
              " estruturada."
          )

          resposta = client.beta.chat.completions.parse(
              model="gpt-4o",
              messages=[
                  {"role": "system", "content": prompt_sistema},
                  {
                      "role": "user",
                      "content": [
                          {"type": "text", "text": prompt_usuario},
                          {
                              "type": "image_url",
                              "image_url": {
                                  "url": (
                                      f"data:image/jpeg;base64,{imagem_base64}"
                                  )
                              },
                          },
                      ],
                  },
              ],
              response_format=CorrecaoProva,
          )

          correcao = resposta.choices[0].message.parsed
          st.success("Correção realizada com sucesso!")

          # Salva no arquivo CSV local
          data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          novo_registro = {
              "Data_Hora": data_hora_atual,
              "Aluno": nome_aluno,
              "Arquivo": arquivo_enviado.name,
              "Nota_Atribuida": correcao.nota_atribuida,
              "Nota_Maxima": correcao.nota_maxima,
              "Pontos_Fortes": " | ".join(correcao.pontos_fortes),
              "Erros_Cometidos": " | ".join(correcao.erros_cometidos),
              "Feedback": correcao.feedback_construtivo,
          }

          arquivo_existe = os.path.exists(ARQUIVO_CSV)
          with open(ARQUIVO_CSV, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=novo_registro.keys())
            if not arquivo_existe:
              writer.writeheader()
            writer.writerow(novo_registro)

          st.toast(
              f"Registro salvo automaticamente em `{ARQUIVO_CSV}`!", icon="📁"
          )

          # Exibição dos resultados da prova atual
          st.markdown("---")
          col1, col2 = st.columns(2)
          with col1:
            st.metric(
                label="Nota Atribuída",
                value=f"{correcao.nota_atribuida} / {correcao.nota_maxima}",
            )

          st.markdown("### 📋 Relatório Detalhado da Prova")
          st.markdown("**Pontos Fortes:**")
          for p in correcao.pontos_fortes:
            st.markdown(f"- ✅ {p}")

          st.markdown("**Erros Cometidos:**")
          for e in correcao.erros_cometidos:
            st.markdown(f"- ❌ {e}")

          st.markdown("**Feedback Construtivo:**")
          st.info(correcao.feedback_construtivo)

          # Botão para baixar PDF Individual
          pdf_buffer = gerar_pdf_relatorio(nome_aluno, correcao)
          st.download_button(
              label="📄 Baixar Relatório Individual em PDF",
              data=pdf_buffer,
              file_name=f"Relatorio_{nome_aluno.replace(' ', '_')}.pdf",
              mime="application/pdf",
          )

        except Exception as e:
          st.error(f"Erro ao processar a prova: {e}")

# --- DASHBOARD E ESTATÍSTICAS DA TURMA (PLOTLY & RELATÓRIO CONSOLIDADO) ---
if os.path.exists(ARQUIVO_CSV):
  st.markdown("---")
  st.subheader("📈 Dashboard Estatístico da Turma")

  df_historico = pd.read_csv(ARQUIVO_CSV)

  if not df_historico.empty:
    total_provas = len(df_historico)
    media_geral = df_historico["Nota_Atribuida"].mean()
    nota_max_alcancada = df_historico["Nota_Atribuida"].max()
    nota_min_alcancada = df_historico["Nota_Atribuida"].min()

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
      st.metric("Provas Corrigidas", total_provas)
    with col_kpi2:
      st.metric("Média da Turma", f"{media_geral:.2f}")
    with col_kpi3:
      st.metric("Maior Nota", f"{nota_max_alcancada:.2f}")
    with col_kpi4:
      st.metric("Menor Nota", f"{nota_min_alcancada:.2f}")

    st.markdown("---")

    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
      st.markdown("#### 📊 Distribuição de Notas (Histograma)")
      fig_hist = px.histogram(
          df_historico,
          x="Nota_Atribuida",
          nbins=10,
          title="Frequência de Notas na Turma",
          labels={
              "Nota_Atribuida": "Nota Atribuída",
              "count": "Número de Alunos",
          },
          color_discrete_sequence=["#4F46E5"],
      )
      fig_hist.update_layout(bargap=0.1)
      st.plotly_chart(fig_hist, width="stretch")

    with col_graf2:
      st.markdown("#### 📦 Dispersão Estatística (Boxplot)")
      fig_box = px.box(
          df_historico,
          y="Nota_Atribuida",
          title="Visão Estatística (Boxplot das Notas)",
          labels={"Nota_Atribuida": "Nota Atribuída"},
          color_discrete_sequence=["#10B981"],
          points="all",
      )
      st.plotly_chart(fig_box, width="stretch")

    st.markdown("#### 📋 Histórico Consolidado de Notas")
    st.dataframe(df_historico, width="stretch")

    col_down1, col_down2 = st.columns(2)
    with col_down1:
      with open(ARQUIVO_CSV, "rb") as f:
        st.download_button(
            label="📥 Baixar Planilha Completa (CSV)",
            data=f,
            file_name="historico_correcoes.csv",
            mime="text/csv",
        )
    with col_down2:
      pdf_turma_buffer = gerar_pdf_consolidado_turma(ARQUIVO_CSV)
      if pdf_turma_buffer:
        st.download_button(
            label="📄 Baixar Relatório Consolidado da Turma (PDF)",
            data=pdf_turma_buffer,
            file_name="relatorio_consolidado_turma.pdf",
            mime="application/pdf",
        )