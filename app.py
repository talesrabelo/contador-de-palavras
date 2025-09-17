import streamlit as st
import random

# Função para inicializar ou reiniciar o jogo
# Usamos o st.session_state para manter as variáveis entre as execuções
def initialize_game():
    st.session_state.secret_number = random.randint(1, 100)
    st.session_state.attempts = 0
    st.session_state.max_attempts = 10
    st.session_state.game_over = False
    st.session_state.message_history = [] # Para guardar o histórico de palpites

# --- Configuração da Página ---
st.set_page_config(page_title="Adivinhe o Número", page_icon="🎲")
st.title("🎲 Adivinhe o Número 🎲")

# Inicializa o jogo na primeira execução ou se 'secret_number' não estiver no estado
if 'secret_number' not in st.session_state:
    initialize_game()

# --- Interface do Jogo ---

# Se o jogo acabou (ganhou ou perdeu), mostra o botão de reiniciar
if st.session_state.game_over:
    st.write("---")
    # O botão "Jogar Novamente" chama a função de inicialização
    if st.button("Jogar Novamente"):
        initialize_game()
        # st.rerun() força o script a rodar novamente com o estado limpo
        st.rerun()

# Se o jogo está em andamento
else:
    remaining_attempts = st.session_state.max_attempts - st.session_state.attempts
    st.write(f"Eu pensei em um número entre 1 e 100.")
    st.write(f"Você tem **{remaining_attempts}** tentativas restantes.")
    
    with st.form("guess_form", clear_on_submit=True):
        guess = st.number_input("Qual é o seu palpite?", min_value=1, max_value=100, step=1, key="guess_input")
        submit_button = st.form_submit_button("Adivinhar")

    if submit_button:
        st.session_state.attempts += 1
        message = "" 

        if guess < st.session_state.secret_number:
            message = f"Palpite {guess}: ⬆️ Muito baixo!"
        elif guess > st.session_state.secret_number:
            message = f"Palpite {guess}: ⬇️ Muito alto!"
        else:
            message = f"🎉 Parabéns! Você adivinhou o número {st.session_state.secret_number} em {st.session_state.attempts} tentativas."
            st.session_state.game_over = True
            st.balloons() 
        
        st.session_state.message_history.append(message)

        if st.session_state.attempts >= st.session_state.max_attempts and not st.session_state.game_over:
            message = f"Fim de jogo! Você usou todas as {st.session_state.max_attempts} tentativas. O número era {st.session_state.secret_number}."
            st.session_state.message_history.append(message)
            st.session_state.game_over = True
        
        st.rerun()

# --- Exibição do Histórico ---
if st.session_state.message_history:
    st.write("---")
    st.subheader("Histórico de Palpites")
    
    for msg in reversed(st.session_state.message_history):
        if "Parabéns" in msg:
            st.success(msg)
        elif "Fim de jogo" in msg:
            st.error(msg)
        else:
            st.info(msg)
