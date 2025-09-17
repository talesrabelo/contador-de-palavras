import streamlit as st
import pandas as pd
import re # Para limpeza de texto (Regex)
import plotly.express as px # Importando o Plotly

# --- Configuração da Página ---
st.set_page_config(page_title="Contador de Palavras", page_icon="📊")
st.title("📊 Analisador de Frequência de Palavras")
st.write("Cole um texto e descubra quantas vezes palavras específicas aparecem.")

# --- 1. Campo para colocar o texto ---
st.header("1. Insira seu texto")
text_input = st.text_area("Cole o texto que você deseja analisar abaixo:", height=200,
                          placeholder="Era uma vez...")

# --- 2. Campos de Configuração (Parte 1: Fora do Formulário) ---
st.header("2. Configure sua Análise")

st.subheader("Quantas palavras você quer contar?")
num_words = st.number_input(
    "Selecione o número de palavras:",
    min_value=1,
    max_value=50, 
    value=3,      
    step=1
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

# --- 3. Processamento e Exibição dos Resultados ---
if submit_button:
    
    if not text_input:
        st.error("Por favor, insira um texto para analisar.")
    else:
        words_to_count = [w.strip().lower() for w in words_to_count_inputs if w.strip()]
        
        if not words_to_count:
            st.error("Por favor, preencha as palavras que deseja contar.")
        else:
            # --- Início do Processamento do Texto ---
            clean_text = text_input.lower()
            all_words_in_text = re.findall(r'\b\w+\b', clean_text)
            
            results = {}
            for word in words_to_count:
                count = all_words_in_text.count(word)
                results[word] = count
            
            # --- Fim do Processamento ---
            
            # Se nenhum resultado for encontrado, não continue
            if all(v == 0 for v in results.values()):
                st.warning("Nenhuma das palavras especificadas foi encontrada no texto.")
            else:
                df = pd.DataFrame(
                    list(results.items()),
                    columns=["Palavra", "Frequência"]
                )
                # Filtra palavras que não foram encontradas (frequência 0)
                df = df[df["Frequência"] > 0] 
                
                df = df.sort_values(by="Frequência", ascending=False).reset_index(drop=True)
                
                st.header("Resultados da Análise")
                
                # --- Saída 1: Tabela de Frequência ---
                st.subheader("Tabela de Frequência")
                st.dataframe(df, use_container_width=True)
                
                # --- Saída 2: Gráfico de Barras ---
                st.subheader("Gráfico de Frequência")
                
                # --- NOVO: Seletor de Gráfico ---
                chart_type = st.selectbox(
                    "Selecione o tipo de gráfico:",
                    [
                        "Barras (Vertical)", 
                        "Barras (Horizontal)", 
                        "Pizza", 
                        "Rosca (Donut)", 
                        "Mapa de Árvore (Treemap)"
                    ]
                )
                
                st.info(
                    "Nota: Gráficos 'Empilhados' e 'Funil' não são aplicáveis a este tipo de dado "
                    "(frequência simples) e, por isso, não estão na lista."
                )

                fig = None # Inicializa a figura

                try:
                    # --- Lógica para desenhar o gráfico selecionado ---
                    if chart_type == "Barras (Vertical)":
                        fig = px.bar(df, 
                                     x="Palavra", 
                                     y="Frequência", 
                                     title="Frequência de Palavras",
                                     color="Palavra",
                                     text_auto=True) # Mostra o valor na barra

                    elif chart_type == "Barras (Horizontal)":
                        # Para barras horizontais, é melhor inverter os eixos
                        fig = px.bar(df.sort_values(by="Frequência", ascending=True), # Inverte a ordem
                                     x="Frequência", 
                                     y="Palavra", 
                                     orientation='h', 
                                     title="Frequência de Palavras",
                                     color="Palavra",
                                     text_auto=True)

                    elif chart_type == "Pizza":
                        fig = px.pie(df, 
                                     names="Palavra", 
                                     values="Frequência", 
                                     title="Distribuição de Palavras (Pizza)")
                        fig.update_traces(textposition='inside', textinfo='percent+label+value')

                    elif chart_type == "Rosca (Donut)":
                        fig = px.pie(df, 
                                     names="Palavra", 
                                     values="Frequência", 
                                     title="Distribuição de Palavras (Rosca)", 
                                     hole=0.4) # A mágica do "buraco"
                        fig.update_traces(textposition='inside', textinfo='percent+label+value')

                    elif chart_type == "Mapa de Árvore (Treemap)":
                        fig = px.treemap(df, 
                                         path=[px.Constant("Todas"), "Palavra"], # Cria a hierarquia
                                         values="Frequência", 
                                         title="Distribuição de Palavras (Mapa de Árvore)",
                                         color="Palavra")
                        fig.update_traces(textinfo="label+value+percent root")
                    
                    # Exibe a figura do Plotly no Streamlit
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Não foi possível gerar o gráfico: {e}")

# --- 4. RODAPÉ DE CRÉDITOS ---
st.divider() 
st.markdown("""
Elaborado por Tales Rabelo Freitas  
LinkedIn: [https://www.linkedin.com/in/tales-rabelo-freitas-1a1466187/](https://www.linkedin.com/in/tales-rabelo-freitas-1a1466187/)
""")
