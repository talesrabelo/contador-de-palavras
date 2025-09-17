import streamlit as st
import pandas as pd
import re # Para limpeza de texto (Regex)

# --- Configuração da Página ---
st.set_page_config(page_title="Contador de Palavras", page_icon="📊")
st.title("📊 Analisador de Frequência de Palavras")
st.write("Cole um texto e descubra quantas vezes palavras específicas aparecem.")

# --- 1. Campo para colocar o texto ---
st.header("1. Insira seu texto")
text_input = st.text_area("Cole o texto que você deseja analisar abaixo:", height=200,
                          placeholder="Era uma vez...")

# --- 2. Campos de Configuração (dentro de um formulário) ---
st.header("2. Configure sua Análise")

# O st.form agrupa os campos e só envia os dados quando o botão é clicado
with st.form("analysis_form"):
    
    # --- Campo 2: Selecionar o número de palavras ---
    st.subheader("Quantas palavras você quer contar?")
    num_words = st.number_input(
        "Selecione o número de palavras:",
        min_value=1,
        max_value=50, # Limite razoável para não poluir a UI
        value=3,      # Valor padrão
        step=1
    )
    
    # --- Campo 3: Preencher com as palavras desejadas ---
    st.subheader("Quais palavras você quer contar?")
    st.caption("A contagem ignora maiúsculas/minúsculas e pontuação (ex: 'Casa' conta 'casa!' e 'casa.').")
    
    words_to_count_inputs = []
    
    # Cria campos de texto dinamicamente baseado no num_words
    # Usamos colunas para organizar melhor se forem muitas palavras
    cols = st.columns(3) # Organiza os inputs em 3 colunas
    for i in range(num_words):
        with cols[i % 3]: # Distribui os inputs entre as 3 colunas
            word = st.text_input(f"Palavra {i+1}", key=f"word_{i}")
            words_to_count_inputs.append(word)
    
    # Botão de envio do formulário
    submit_button = st.form_submit_button("Analisar Frequência")

# --- 3. Processamento e Exibição dos Resultados ---
# Esta parte só executa se o botão "Analisar" for pressionado
if submit_button:
    
    # Validação 1: Verificar se o texto foi inserido
    if not text_input:
        st.error("Por favor, insira um texto para analisar.")
    else:
        # Limpeza das palavras-alvo: remove espaços e converte para minúsculas
        # Filtra strings vazias caso o usuário não preencha todos os campos
        words_to_count = [w.strip().lower() for w in words_to_count_inputs if w.strip()]
        
        # Validação 2: Verificar se as palavras-alvo foram preenchidas
        if not words_to_count:
            st.error("Por favor, preencha as palavras que deseja contar.")
        else:
            # --- Início do Processamento do Texto ---
            
            # 1. Converte o texto principal para minúsculas
            clean_text = text_input.lower()
            
            # 2. Encontra todas as "palavras" (sequências de letras/números)
            #    Isso remove pontuações como '!' ',' '.' etc.
            #    \b = limite da palavra, \w+ = um ou mais caracteres de palavra
            all_words_in_text = re.findall(r'\b\w+\b', clean_text)
            
            # 3. Contagem
            results = {}
            for word in words_to_count:
                # Conta as ocorrências da palavra (já em minúsculo) na lista de palavras
                count = all_words_in_text.count(word)
                results[word] = count
            
            # --- Fim do Processamento ---
            
            # Cria um DataFrame (tabela) do Pandas com os resultados
            df = pd.DataFrame(
                list(results.items()),
                columns=["Palavra", "Frequência"]
            )
            
            # Ordena o DataFrame da mais frequente para a menos frequente
            df = df.sort_values(by="Frequência", ascending=False).reset_index(drop=True)
            
            st.header("Resultados da Análise")
            
            # --- Saída 1: Tabela de Frequência ---
            st.subheader("Tabela de Frequência")
            st.dataframe(df, use_container_width=True)
            
            # --- Saída 2: Gráfico de Barras ---
            st.subheader("Gráfico de Frequência")
            
            # Prepara o DataFrame para o gráfico (Palavra como índice)
            # Isso é necessário para o st.bar_chart saber o que colocar no eixo X
            try:
                chart_df = df.set_index("Palavra")
                st.bar_chart(chart_df)
            except Exception as e:
                st.error(f"Não foi possível gerar o gráfico: {e}")
