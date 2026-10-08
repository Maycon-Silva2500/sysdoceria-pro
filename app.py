import streamlit as st
import pandas as pd
import os

# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha)
# Layout wide e barra lateral oculta por padrão (clean look)
st.set_page_config(page_title="SysDoceria PRO", page_icon="🧁", layout="wide", initial_sidebar_state="collapsed")

# 2. INJEÇÃO DE CSS (Design Premium e Responsivo)
st.markdown("""
    <style>
        /* Reduzir o espaçamento no topo para ecrãs pequenos */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* Ocultar elementos padrão do Streamlit (cabeçalho, rodapé e menu) */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Estilizar os cartões de Métricas (Dashboard) */
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* Estilizar os botões primários */
        .stButton > button[kind="primary"] {
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(219, 39, 119, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# 3. BANCO DE DADOS (CSV)
ARQ_PRODUTOS = "produtos.csv"
ARQ_INGREDIENTES = "ingredientes.csv"

def carregar_produtos():
    if not os.path.exists(ARQ_PRODUTOS):
        pd.DataFrame(columns=["Produto", "Categoria", "Preço"]).to_csv(ARQ_PRODUTOS, index=False)
    return pd.read_csv(ARQ_PRODUTOS)

def carregar_ingredientes():
    if not os.path.exists(ARQ_INGREDIENTES):
        pd.DataFrame(columns=["Ingrediente", "Unidade", "Quantidade", "Preço", "Custo_Unitario"]).to_csv(ARQ_INGREDIENTES, index=False)
    return pd.read_csv(ARQ_INGREDIENTES)

def salvar_produtos(df):
    df.to_csv(ARQ_PRODUTOS, index=False)

def salvar_ingredientes(df):
    df.to_csv(ARQ_INGREDIENTES, index=False)

# 4. CABEÇALHO DO SISTEMA
st.title("🧁 SysDoceria PRO")
st.markdown("<p style='color: #6b7280; font-size: 15px; margin-top: -15px;'>O seu sistema inteligente de gestão, custos e precificação.</p>", unsafe_allow_html=True)
st.write("") # Espaçamento

# 5. NAVEGAÇÃO RESPONSIVA (ABAS)
aba_geral, aba_calc, aba_prod, aba_ing = st.tabs([
    "📊 Visão Geral", 
    "🧮 Ficha Técnica", 
    "🍰 Produtos", 
    "🛒 Insumos"
])

# --- ABA 1: VISÃO GERAL ---
with aba_geral:
    df_prod = carregar_produtos()
    df_ing = carregar_ingredientes()
    
    # As colunas empilham-se automaticamente no telemóvel
    col1, col2 = st.columns(2)
    col1.metric("Produtos Ativos no Catálogo", len(df_prod))
    col2.metric("Insumos Base Registados", len(df_ing))
    
    st.markdown("### 📋 Catálogo de Produtos")
    if not df_prod.empty:
        st.caption("Dica: Edite os valores diretamente na tabela abaixo. Para apagar, selecione a linha e pressione 'Delete'.")
        # use_container_width=True garante que a tabela não quebra o layout no telemóvel
        df_editado = st.data_editor(df_prod, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        if st.button("💾 Guardar Alterações da Tabela", type="primary"):
            salvar_produtos(df_editado)
            st.success("Tabela atualizada com sucesso no banco de dados!")
    else:
        st.info("Nenhum produto cadastrado ainda.")

# --- ABA 2: CALCULADORA (FICHA TÉCNICA) ---
with aba_calc:
    if "receita" not in st.session_state:
        st.session_state["receita"] = []
        
    df_ing = carregar_ingredientes()
    
    st.markdown("### Configuração da Receita")
    # No PC ficam lado a lado, no telemóvel ficam um por baixo do outro automaticamente
    c1, c2, c3 = st.columns([2, 1, 1])
    nome_receita = c1.text_input("Nome da Receita", placeholder="Ex: Torta de Limão")
    rendimento = c2.number_input("Rendimento (unid.)", min_value=1, value=1)
    lucro_desejado = c3.number_input("Lucro Desejado (%)", min_value=0.0, value=50.0)
    
    st.markdown("---")
    st.markdown("### Adicionar Insumos")
    
    if df_ing.empty:
        st.warning("⚠️ Precisa de cadastrar ingredientes na aba 'Insumos' primeiro!")
    else:
        opcoes_ing = df_ing.apply(lambda row: f"{row['Ingrediente']} (R$ {row['Custo_Unitario']:.4f} / {row['Unidade']})", axis=1).tolist()
        
        col_ing1, col_ing2, col_ing3 = st.columns([3, 1, 1])
        ing_selecionado = col_ing1.selectbox("Selecione o Insumo", opcoes_ing)
        qtd_usada = col_ing2.number_input("Quantidade", min_value=0.01, value=1.00, step=1.0)
        
        col_ing3.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Espaçamento invisível
        if col_ing3.button("➕ Adicionar"):
            idx = opcoes_ing.index(ing_selecionado)
            ing_data = df_ing.iloc[idx]
            
            st.session_state["receita"].append({
                "Ingrediente": ing_data["Ingrediente"],
                "Qtd Usada": qtd_usada,
                "Custo Total": qtd_usada * ing_data["Custo_Unitario"]
            })
            st.rerun()
            
    if st.session_state["receita"]:
        df_receita = pd.DataFrame(st.session_state["receita"])
        st.dataframe(df_receita, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Limpar Receita"):
            st.session_state["receita"] = []
            st.rerun()
            
        custo_total = df_receita["Custo Total"].sum()
        custo_unitario = custo_total / rendimento
        preco_sugerido = custo_unitario * (1 + (lucro_desejado / 100))
        
        st.markdown("---")
        st.markdown("### 💰 Resumo Financeiro")
        res1, res2, res3 = st.columns(3)
        res1.metric("Custo da Receita", f"R$ {custo_total:.2f}")
        res2.metric("Custo Unitário", f"R$ {custo_unitario:.2f}")
        res3.metric("Preço de Venda Sugerido", f"R$ {preco_sugerido:.2f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Aprovar e Salvar no Catálogo", type="primary", use_container_width=True):
            if not nome_receita:
                st.error("Dê um nome para a receita no topo da página antes de guardar.")
            else:
                df_prod = carregar_produtos()
                novo_prod = pd.DataFrame([{"Produto": nome_receita, "Categoria": "Ficha Técnica", "Preço": round(preco_sugerido, 2)}])
                df_prod = pd.concat([df_prod, novo_prod], ignore_index=True)
                salvar_produtos(df_prod)
                st.session_state["receita"] = []
                st.success(f"Receita '{nome_receita}' adicionada ao catálogo por R$ {preco_sugerido:.2f}!")

# --- ABA 3: PRODUTOS ---
with aba_prod:
    st.markdown("### Cadastrar Produto Manualmente")
    st.caption("Use esta opção para inserir produtos que não precisam de cálculo de ficha técnica.")
    
    with st.form("form_produto", clear_on_submit=True):
        nome = st.text_input("Nome do Produto")
        categoria = st.text_input("Categoria", placeholder="Ex: Bolos, Doces, Bebidas...")
        preco = st.number_input("Preço de Venda Final (R$)", min_value=0.0, step=0.5, format="%.2f")
        
        submit_prod = st.form_submit_button("Guardar Produto", type="primary")
        if submit_prod:
            if nome and categoria:
                df_prod = carregar_produtos()
                novo_prod = pd.DataFrame([{"Produto": nome, "Categoria": categoria, "Preço": preco}])
                df_prod = pd.concat([df_prod, novo_prod], ignore_index=True)
                salvar_produtos(df_prod)
                st.success(f"O produto '{nome}' foi registado com sucesso!")
            else:
                st.error("Preencha o nome e a categoria.")

# --- ABA 4: INSUMOS ---
with aba_ing:
    st.markdown("### Registo de Ingredientes (Compras)")
    st.caption("Cadastre o valor exato que pagou pela embalagem fechada no fornecedor/supermercado.")
    
    with st.form("form_ingrediente", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        nome = c1.text_input("Nome do Insumo (Marca/Produto)")
        unidade = c2.selectbox("Formato de Medida", ["g (Gramas)", "ml (Mililitros)", "un (Unidade)"])
        
        c3, c4 = st.columns(2)
        quantidade = c3.number_input("Quantidade na Embalagem", min_value=0.01, step=1.0, placeholder="Ex: 395")
        preco = c4.number_input("Valor Pago na Embalagem (R$)", min_value=0.01, step=0.5, format="%.2f")
        
        unidade_limpa = unidade.split(" ")[0] # Extrai apenas "g", "ml" ou "un"
        
        submit_ing = st.form_submit_button("Registrar Insumo", type="primary")
        if submit_ing:
            if nome:
                custo_unit = preco / quantidade
                df_ing = carregar_ingredientes()
                novo_ing = pd.DataFrame([{
                    "Ingrediente": nome, 
                    "Unidade": unidade_limpa, 
                    "Quantidade": quantidade, 
                    "Preço": preco, 
                    "Custo_Unitario": custo_unit
                }])
                df_ing = pd.concat([df_ing, novo_ing], ignore_index=True)
                salvar_ingredientes(df_ing)
                st.success(f"Insumo guardado! Custo processado: R$ {custo_unit:.4f} por {unidade_limpa}")
            else:
                st.error("Preencha o nome do insumo.")