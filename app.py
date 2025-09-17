import streamlit as st
import pandas as pd
import re # Para limpeza de texto (Regex)
import plotly.express as px # Importando o Plotly

# --- Configuração da Página ---
st.set_page_config(page_title="Contador de Palavras", page_icon="📊")
st.title("📊 Analisador de Frequência de Palavras")
st.write("Cole um texto e descubra quantas vezes palavras específicas aparecem.")

# Inicializa o 'session_state' para guardar os resultados
if 'df_results' not in st.session_state:
    st.session_state.df_results = None

# Função para limpar os resultados se o texto ou inputs mudarem
def clear_results():
    st.session_state.df_results = None

# --- 1. Campo para colocar o texto ---
st.header("1. Insira seu texto")
text_input = st.text_area("Cole o texto que você deseja analisar abaixo:", height=200,
                          placeholder="Era uma vez...", on_change=clear_results)

# --- 2. Campos de Configuração (Parte 1: Fora do Formulário) ---
st.header("2. Configure sua Análise")

st.subheader("Quantas palavras você quer contar?")
num_words = st.number_input(
    "Selecione o número de palavras:",
    min_value=1,
    max_value=50, 
    value=3,      
    step=1,
    on_change=clear_results # Limpa resultados antigos se mudar o número
)

# --- 2. Campos de Configuração (Parte 2: Dentro do Formulário) ---
with st.form("analysis_form"):
    
    st.subheader("Quais palavras você quer contar?")
    st.caption("A contagem ignora maiúsculas/minúsculas e pontuação (ex: 'Casa' conta 'casa!' e 'casa.').")
    
    words_to_count_inputs = []
    
    cols = st.columns(3) 
    for i in range(num_words):
        with cols[i % 3]: 
            word = st.text_input(f"Palavra {i+1}", key=f"word_{i}")
            words_to_count_inputs.append(word)
    
    submit_button = st.form_submit_button("Analisar Frequência")

# --- 3. Processamento ---
if submit_button:
    
    if not text_input:
        st.error("Por favor, insira um texto para analisar.")
        st.session_state.df_results = None 
    else:
        words_to_count = [w.strip().lower() for w in words_to_count_inputs if w.strip()]
        
        if not words_to_count:
            st.error("Por favor, preencha as palavras que deseja contar.")
            st.session_state.df_results = None 
        else:
            clean_text = text_input.lower()
            all_words_in_text = re.findall(r'\b\w+\b', clean_text)
            
            results = {}
            for word in words_to_count:
                count = all_words_in_text.count(word)
                results[word] = count
            
            if all(v == 0 for v in results.values()):
                st.warning("Nenhuma das palavras especificadas foi encontrada no texto.")
                st.session_state.df_results = None
            else:
                df = pd.DataFrame(
                    list(results.items()),
                    columns=["Palavra", "Frequência"]
                )
                df = df[df["Frequência"] > 0] 
                df = df.sort_values(by="Frequência", ascending=False).reset_index(drop=True)
                
                st.session_state.df_results = df.copy()


# --- 4. Exibição dos Resultados ---
if st.session_state.df_results is not None:
    
    df = st.session_state.df_results 
    
    st.header("Resultados da Análise")
    
    # --- Saída 1: Tabela de Frequência ---
    st.subheader("Tabela de Frequência")
    
    # --- MODIFICAÇÃO AQUI (v2) ---
    # Aplica o estilo CSS de forma mais explícita para cabeçalhos (th) e células (td)
    df_styled = df.style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center')]},
        {'selector': 'td', 'props': [('text-align', 'center')]}
    ])
    
    # Adiciona hide_index=True para remover a coluna de índice (0, 1, 2, 3)
    st.dataframe(df_styled, use_container_width=True, hide_index=True)
    # --- FIM DA MODIFICAÇÃO ---
    
    # --- Saída 2: Gráfico de Frequência ---
    st.subheader("Gráfico de Frequência")
    
    chart_type = st.selectbox(
        "Selecione o tipo de gráfico:",
        [
            "Barras (Vertical)", 
            "Barras (Horizontal)", 
            "Barras Empilhadas (Vertical)",
            "Barras Empilhadas (Horizontal)",
            "Pizza", 
            "Rosca (Donut)", 
            "Mapa de Árvore (Treemap)",
            "Funil"
        ]
    )

    fig = None 

    try:
        if chart_type == "Barras (Vertical)":
            fig = px.bar(df, x="Palavra", y="Frequência", title="Frequência de Palavras",
                         color="Palavra", text_auto=True)

        elif chart_type == "Barras (Horizontal)":
            fig = px.bar(df.sort_values(by="Frequência", ascending=True), 
                         x="Frequência", y="Palavra", orientation='h', title="Frequência de Palavras",
                         color="Palavra", text_auto=True)

        elif chart_type == "Barras Empilhadas (Vertical)":
            df_stack = df.copy()
            df_stack['Eixo'] = 'Frequência Total'
            fig = px.bar(df_stack, x='Eixo', y='Frequência', color='Palavra', 
                         title="Barras Empilhadas (Vertical)", text_auto=True)

        elif chart_type == "Barras Empilhadas (Horizontal)":
            df_stack = df.copy()
            df_stack['Eixo'] = 'Frequência Total'
            fig = px.bar(df_stack, y='Eixo', x='Frequência', color='Palavra', 
                         title="Barras Empilhadas (Horizontal)", orientation='h', text_auto=True)

        elif chart_type == "Pizza":
            fig = px.pie(df, names="Palavra", values="Frequência", 
                         title="Distribuição de Palavras (Pizza)")
            fig.update_traces(textposition='inside', textinfo='percent+label+value')

        elif chart_type == "Rosca (Donut)":
            fig = px.pie(df, names="Palavra", values="Frequência", 
                         title="Distribuição de Palavras (Rosca)", hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label+value')

        elif chart_type == "Mapa de Árvore (Treemap)":
            fig = px.treemap(df, path=[px.Constant("Todas"), "Palavra"], 
                             values="Frequência", title="Distribuição de Palavras (Mapa de Árvore)",
                             color="Palavra")
            fig.update_traces(textinfo="label+value+percent root")
        
        elif chart_type == "Funil":
            fig = px.funnel(df, x='Frequência', y='Palavra', 
                            title='Gráfico de Funil', color='Palavra')

        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Não foi possível gerar o gráfico: {e}")

# --- 5. RODAPÉ DE CRÉDITOS ---
st.divider() 
st.markdown("""
Elaborado por Tales Rabelo Freitas  
LinkedIn: [https://www.linkedin.com/in/tales-rabelo-freitas-1a1466187/](https://www.linkedin.com/in/tales-rabelo-freitas-1a1466187/)
""")
