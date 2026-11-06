Aqui está o código completo e consolidado do seu aplicativo em Streamlit (app.py), reunindo todas as funcionalidades construídas até agora:

Correção Automática com Visão Computacional e LLM (OpenAI GPT-4o via API).

Structured Outputs com Pydantic (garantindo JSON rigoroso para notas, pontos fortes, erros e feedbacks).

Gabarito Dinâmico com st.data_editor (o professor define questões e pesos interativamente na barra lateral).

Salvamento Automático em Histórico CSV (acumulando registros de toda a turma).

Dashboard Estatístico com Plotly (Histogramas interativos e Boxplot de notas).

Geração de Relatórios Individuais em PDF (via ReportLab para cada aluno).

Geração de Relatório Consolidado da Turma em PDF (com KPIs gerais e tabela formatada).

LOGIN DE PROFESSORES (EXECUÇÃO LOCAL)

1. Gere um hash de senha no terminal, dentro da pasta do projeto:
   .\.venv\Scripts\python.exe .\auth.py
   A senha é solicitada sem aparecer na tela. Use uma senha única com pelo
   menos 12 caracteres.
2. Crie ou edite .streamlit/secrets.toml (este arquivo não deve ser publicado):

   OPENAI_API_KEY = "sua-chave-da-openai"

   [auth.users]
   professor1 = "COLE_AQUI_O_HASH_GERADO"

   Adicione outros professores como outras entradas em [auth.users], cada um
   com seu próprio hash.
3. Execute o aplicativo:
   .\.venv\Scripts\python.exe -m streamlit run .\app.py

As senhas são armazenadas como hashes PBKDF2-SHA256, não em texto simples.
Cada professor tem um histórico CSV separado em data/; esses dados e os
secrets são ignorados pelo Git. O histórico antigo historico_correcoes.csv,
se existir, não é associado automaticamente a nenhum professor.

Para conferir um acesso sem exibir a senha, execute:
   .\.venv\Scripts\python.exe .\verificar_login.py
