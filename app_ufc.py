import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64
# 
# CONFIGURACIÓN DE LA PÁGINA Y CSS (Cyber-Tech)
# 
st.set_page_config(page_title="UFC Freedom 250 - Oráculo", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1 { color: #D20000; font-family: 'Arial Black', sans-serif; text-transform: uppercase; text-align: center; letter-spacing: 2px;}
    h2, h3 { color: #FFFFFF; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .ganador-texto { color: #D4AF37; font-size: 32px; font-weight: bold; text-align: center; padding: 10px; border-top: 2px solid #D20000; border-bottom: 2px solid #D20000; margin-bottom: 20px;}
    .probabilidad-under-name { color: #D4AF37; font-size: 20px; font-weight: bold; text-align: center; margin-top: -15px; margin-bottom: 5px;}
    .probabilidad-under-name-small { color: #D4AF37; font-size: 14px; font-weight: bold; text-align: center; margin-top: -8px; margin-bottom: 5px;}
    .stats-micro { font-size: 13px; text-align: center; color: #BBBBBB; margin-top: -5px; line-height: 1.2; }
    .stProgress > div > div > div > div { background-color: #D20000; }
    .porcentaje-label { font-size: 18px; font-weight: bold; color: #CCCCCC; margin-bottom: -10px; }
    .analisis-caja { background-color: #1A1C23; padding: 20px; border-radius: 8px; border-left: 5px solid #D4AF37; font-size: 16px; line-height: 1.6;}
    </style>
""", unsafe_allow_html=True)


# Generador de bolitas de racha
def renderizar_racha(last_5):
    html = "<div style='text-align: center; margin-bottom: 10px;'>"
    for res in last_5:
        color = "#00FF00" if res == 'W' else "#FF0000"
        html += f"<span style='display: inline-block; width: 12px; height: 12px; background-color: {color}; border-radius: 50%; margin: 0 3px; box-shadow: 0 0 5px {color};'></span>"
    html += "</div>"
    return html


# BASE DE DATOS AUDITADA
# 
mapa_imagenes = {
    "Ilia Topuria": "ILIA_TOPURIA.avif", "Justin Gaethje": "JUSTIN GAETHJE.avif",
    "Alex Pereira": "ALEX_PEREIRA.avif", "Ciryl Gane": "CIRYL_GANE.avif",
    "Sean O'Malley": "sean_o'malley.avif", "Aiemann Zahabi": "AIEMANN_ZAHABI.avif",
    "Bo Nickal": "BO_NICKAL.avif", "Kyle Daukaus": "KYLE_DAUKAUS.avif",
    "Diego Lopes": "DIEGO_LOPES.avif", "Steve Garcia": "STEVE_GARCIA.avif",
    "Mauricio Ruffy": "MAURICIO_RUFFY.avif", "Michael Chandler": "MICHAEL_CHANDLER.avif"
}

peleadores = {
    "Ilia Topuria": {"wins": 17, "losses": 0, "slpm": 4.81, "sapm": 3.83, "str_def": 0.64, "td_avg": 1.96, "td_def": 0.94, "reach": 69, "age": 29, "ko_ratio": 0.41, "sub_ratio": 0.47, "dec_ratio": 0.12, "last_5": ['W', 'W', 'W', 'W', 'W']},
    "Justin Gaethje": {"wins": 27, "losses": 5, "slpm": 6.48, "sapm": 7.05, "str_def": 0.51, "td_avg": 0.13, "td_def": 0.74, "reach": 70, "age": 37, "ko_ratio": 0.74, "sub_ratio": 0.04, "dec_ratio": 0.22, "last_5": ['L', 'W', 'W', 'L', 'W']},
    "Alex Pereira": {"wins": 13, "losses": 3, "slpm": 5.16, "sapm": 3.50, "str_def": 0.54, "td_avg": 0.11, "td_def": 0.79, "reach": 79, "age": 38, "ko_ratio": 0.85, "sub_ratio": 0.00, "dec_ratio": 0.15, "last_5": ['W', 'W', 'W', 'W', 'W']},
    "Ciryl Gane": {"wins": 13, "losses": 2, "slpm": 5.29, "sapm": 2.33, "str_def": 0.61, "td_avg": 0.60, "td_def": 0.47, "reach": 81, "age": 35, "ko_ratio": 0.46, "sub_ratio": 0.23, "dec_ratio": 0.31, "last_5": ['W', 'L', 'W', 'L', 'W']},
    "Sean O'Malley": {"wins": 19, "losses": 3, "slpm": 6.05, "sapm": 3.40, "str_def": 0.60, "td_avg": 0.24, "td_def": 0.61, "reach": 72, "age": 31, "ko_ratio": 0.63, "sub_ratio": 0.05, "dec_ratio": 0.32, "last_5": ['L', 'W', 'W', 'W', 'W']},
    "Aiemann Zahabi": {"wins": 14, "losses": 2, "slpm": 4.54, "sapm": 4.08, "str_def": 0.69, "td_avg": 0.12, "td_def": 0.83, "reach": 68, "age": 38, "ko_ratio": 0.43, "sub_ratio": 0.14, "dec_ratio": 0.43, "last_5": ['W', 'W', 'W', 'W', 'W']},
    "Bo Nickal": {"wins": 8, "losses": 1, "slpm": 3.35, "sapm": 2.07, "str_def": 0.59, "td_avg": 3.10, "td_def": 1.00, "reach": 76, "age": 30, "ko_ratio": 0.25, "sub_ratio": 0.75, "dec_ratio": 0.00, "last_5": ['W', 'W', 'W', 'W', 'W']},
    "Kyle Daukaus": {"wins": 17, "losses": 4, "slpm": 3.32, "sapm": 2.90, "str_def": 0.42, "td_avg": 2.08, "td_def": 0.82, "reach": 76, "age": 33, "ko_ratio": 0.05, "sub_ratio": 0.65, "dec_ratio": 0.30, "last_5": ['W', 'L', 'W', 'L', 'W']},
    "Diego Lopes": {"wins": 27, "losses": 8, "slpm": 3.83, "sapm": 4.56, "str_def": 0.45, "td_avg": 0.88, "td_def": 0.68, "reach": 72, "age": 31, "ko_ratio": 0.37, "sub_ratio": 0.44, "dec_ratio": 0.19, "last_5": ['W', 'W', 'W', 'W', 'W']},
    "Steve Garcia": {"wins": 19, "losses": 5, "slpm": 5.39, "sapm": 2.12, "str_def": 0.59, "td_avg": 0.86, "td_def": 0.88, "reach": 75, "age": 33, "ko_ratio": 0.82, "sub_ratio": 0.00, "dec_ratio": 0.18, "last_5": ['W', 'W', 'W', 'W', 'W']},
    "Mauricio Ruffy": {"wins": 13, "losses": 2, "slpm": 4.90, "sapm": 3.10, "str_def": 0.52, "td_avg": 1.10, "td_def": 0.70, "reach": 73, "age": 30, "ko_ratio": 0.90, "sub_ratio": 0.00, "dec_ratio": 0.10, "last_5": ['W', 'W', 'W', 'W', 'W']},
    "Michael Chandler": {"wins": 23, "losses": 10, "slpm": 4.04, "sapm": 4.52, "str_def": 0.43, "td_avg": 1.96, "td_def": 0.61, "reach": 71, "age": 39, "ko_ratio": 0.48, "sub_ratio": 0.30, "dec_ratio": 0.22, "last_5": ['L', 'L', 'W', 'L', 'L']}
}

cartelera = [
    ("Ilia Topuria", "Justin Gaethje"), ("Alex Pereira", "Ciryl Gane"),
    ("Sean O'Malley", "Aiemann Zahabi"), ("Bo Nickal", "Kyle Daukaus"),
    ("Diego Lopes", "Steve Garcia"), ("Mauricio Ruffy", "Michael Chandler")
]

# 
# MOTOR ANALITICO  


def graficar_striking(fA_name, fB_name, sA, sB):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=['Ofensiva (Golpes Lanzados)', 'Defensiva (Golpes Recibidos)'], 
                         y=[sA['slpm'], sA['sapm']], name=fA_name, marker_color='#D4AF37'))
    fig.add_trace(go.Bar(x=['Ofensiva (Golpes Lanzados)', 'Defensiva (Golpes Recibidos)'], 
                         y=[sB['slpm'], sB['sapm']], name=fB_name, marker_color='#D20000'))
    
    fig.update_layout(
        title="Diferencial de Striking (SLpM vs SApM)",
        template="plotly_dark", barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def generar_texto_analitico(pelea_id, fA, fB, ganador):
    texto = ""
    if pelea_id == "Ilia Topuria vs Justin Gaethje":
        texto = f"**La Ecuación del Daño y Juventud:** El algoritmo proyecta una victoria contundente para Topuria basándose en el déficit defensivo de su rival. Justin Gaethje es un peleador de alto volumen, pero es una esponja de daño (absorbe {fB['sapm']} golpes/minuto frente a los {fA['sapm']} de Ilia). Topuria no solo tiene una defensa de striking superior ({fA['str_def']*100}%), sino que su sólida defensa de derribos del {fA['td_def']*100}% obligará a Gaethje (37 años) a un intercambio de boxeo prolongado contra un noqueador letal de 29 años, donde el desgaste neurológico será matemáticamente insostenible."
    elif pelea_id == "Alex Pereira vs Ciryl Gane":
        texto = f"**Precisión Evasiva vs. Poder Absoluto:** Aunque 'Poatan' posee un poder de KO devastador, el modelo heurístico favorece la inteligencia espacial y gestión de distancia de Gane. El francés ostenta una excelente defensa de golpeo ({fB['str_def']*100}%) y absorbe apenas {fB['sapm']} golpes por minuto. Pereira recibe significativamente más castigo ({fA['sapm']}). Matemáticamente, Gane dictará el ritmo desde el perímetro, conectando mayor volumen de golpes limpios y minimizando la ventana de oportunidad para el letal gancho izquierdo del brasileño."
    elif pelea_id == "Sean O'Malley vs Aiemann Zahabi":
        texto = f"**Volumen Ofensivo y Control de Distancia:** 'Suga' Sean es un francotirador estadístico que lanza {fA['slpm']} golpes significativos por minuto, superando ampliamente los {fB['slpm']} de Zahabi. Para que Zahabi (38 años) tenga éxito, necesitaría llevar la pelea a la lona, pero su promedio de derribos es muy bajo ({fB['td_avg']}) y choca frontalmente contra la defensa de derribos del {fA['td_def']*100}% de O'Malley. El modelo predice que Sean mantendrá la pelea de pie, desarmando la guardia de Zahabi con su ventaja de alcance y volumen."
    elif pelea_id == "Bo Nickal vs Kyle Daukaus":
        texto = f"**Dominio Absoluto en el Grappling:** Este es un choque de estilos donde la lucha libre élite dicta la probabilidad. Nickal promedia unos aplastantes {fA['td_avg']} derribos por pelea y ostenta un impecable 100% histórico de defensa contra derribos. Aunque Daukaus es competente, el modelo proyecta que no podrá frenar la presión inicial. Al absorber apenas {fA['sapm']} golpes por minuto, Bo cerrará la distancia sin recibir daño y controlará el combate en la lona de principio a fin."
    elif pelea_id == "Diego Lopes vs Steve Garcia":
        texto = f"**Guerra de Desgaste y Defensa:** El modelo detecta una vulnerabilidad crítica en la guardia de Lopes: absorbe {fA['sapm']} golpes significativos por minuto. Enfrente tiene a Steve Garcia, un peleador con un volumen ofensivo letal ({fB['slpm']} SLpM) que además defiende mejor los ataques ({fB['sapm']} SApM). En un intercambio sostenido de striking puro, la métrica proyecta que el volumen constante y la mejor gestión del daño de Garcia terminarán quebrando la resistencia del brasileño."
    elif pelea_id == "Mauricio Ruffy vs Michael Chandler":
        texto = f"**El Factor Decadencia (Edad vs Juventud):** La ciencia de datos en las MMA castiga severamente a los peleadores mayores en divisiones ligeras. Michael Chandler (39 años) tiene un estilo temerario que le hace absorber {fB['sapm']} golpes por minuto. Ruffy (30 años) llega con un altísimo ratio de finalización. El algoritmo anticipa que, aunque Chandler saldrá explosivo buscando derribos ({fB['td_avg']} TD Avg), los huecos defensivos que deja al atacar serán capitalizados rápidamente por el striking fresco del brasileño."
    
    # Agregamos el Momentum al final si aplica
    racha_A, racha_B = fA['last_5'].count('W'), fB['last_5'].count('W')
    if racha_A > racha_B and ganador in pelea_id.split(" vs ")[0]:
        texto += f" Además, el 'Momentum' estadístico de sus últimas 5 peleas consolida la confianza de {ganador} para asegurar la victoria."
    elif racha_B > racha_A and ganador in pelea_id.split(" vs ")[1]:
        texto += f" Además, el 'Momentum' estadístico de sus últimas 5 peleas consolida la confianza de {ganador} para asegurar la victoria."
        
    return texto

def calcular_combate(fA_name, fB_name):
    fA, fB = peleadores[fA_name], peleadores[fB_name]
    score_A, score_B = 100.0, 100.0
    
    score_A += (fA['slpm'] * (1 - fB['str_def']) * 5) - ((fA['sapm'] * 2 if fA['sapm'] > 5.0 else fA['sapm']) * 4)
    score_B += (fB['slpm'] * (1 - fA['str_def']) * 5) - ((fB['sapm'] * 2 if fB['sapm'] > 5.0 else fB['sapm']) * 4)
    
    score_A += fA['td_avg'] * (1 - fB['td_def']) * 10
    score_B += fB['td_avg'] * (1 - fA['td_def']) * 10
    
    diff_edad = fA['age'] - fB['age']
    if diff_edad < -3: score_A += abs(diff_edad) * 2.5 
    elif diff_edad > 3: score_A -= abs(diff_edad) * 2.5
    score_A += (fA['reach'] - fB['reach']) * 1.5
    
    score_A += (fA['wins'] / (fA['wins'] + fA['losses'])) * 15
    score_B += (fB['wins'] / (fB['wins'] + fB['losses'])) * 15
    
    score_A += fA['last_5'].count('W') * 2.5
    score_B += fB['last_5'].count('W') * 2.5
    
    total = max(score_A, 0.1) + max(score_B, 0.1)
    prob_A, prob_B = score_A / total, score_B / total
    
    if prob_A >= prob_B: ganador, p_win, stats_g = fA_name, prob_A, fA
    else: ganador, p_win, stats_g = fB_name, prob_B, fB
        
    p_ko = p_win * stats_g['ko_ratio']
    p_sub = p_win * stats_g['sub_ratio']
    p_dec = p_win * stats_g['dec_ratio']
    
    analisis = generar_texto_analitico(f"{fA_name} vs {fB_name}", fA, fB, ganador)
        
    return ganador, p_win, p_ko, p_sub, p_dec, analisis, prob_A, prob_B, fA, fB

# 
# INTERFAZ DE USUARIO (FRONT-END)

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/9/92/UFC_Logo.svg", width=150)
st.sidebar.markdown("## ⚙️ PANEL DE CONTROL")
modo_vista = st.sidebar.radio("Modo de Visualización:", ["Cartelera Completa", "Análisis Individual Profundo"])

# 
# CRÉDITOS Y ENLACES LOCALES (Top Right)
# 
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

ruta_linkedin = "Imagenes/linkedin.png"
ruta_portafolio = "Imagenes/portfolio.png"

if os.path.exists(ruta_linkedin) and os.path.exists(ruta_portafolio):
    img_lk = get_base64(ruta_linkedin)
    img_pt = get_base64(ruta_portafolio)
    
    # HTML sin el filtro de escala de grises, con un sutil efecto de zoom al pasar el mouse
    html_creditos = f"""
<div style='text-align: right; margin-top: -40px; margin-bottom: 20px;'>
    <span style='color: #D4AF37; font-size: 14px; font-weight: bold; margin-right: 15px; letter-spacing: 1px;'>
        CREADO POR ING. DARIEL PEÑA 
        <P>Click  Portafolio web  👉
    </span>
    <a href='https://portafolio-dariel-delta.vercel.app/' target='_blank'>
        <img src='data:image/png;base64,{img_pt}' width='26' style='transition: 0.3s;' onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
    </a>
    <a href='https://www.linkedin.com/in/darielpe%C3%B1av%C3%A1squez/' target='_blank'>
        <img src='data:image/png;base64,{img_lk}' width='26' style='margin-right: 10px; transition: 0.3s;' onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
    </a>
</div>
"""
    st.markdown(html_creditos, unsafe_allow_html=True)
else:
    st.warning("⚠️ Faltan los íconos de LinkedIn o Portafolio en la carpeta 'imagenes'.")

# TÍTULO ÉPICO (Puesto una sola vez)
st.markdown("<h1>⚔️ UFC FREEDOM 250: BATTLE AT THE WHITE HOUSE ⚔️</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #888; margin-top: -15px; margin-bottom: 40px;'>ANÁLISIS PREDICTIVO-DARIEL.P</h3>", unsafe_allow_html=True)
# 
# MODO 1: CARTELERA COMPLETA
# 
if modo_vista == "Cartelera Completa":
    for fA_name, fB_name in cartelera:
        ganador, p_win, p_ko, p_sub, p_dec, analisis, pA_raw, pB_raw, fA, fB = calcular_combate(fA_name, fB_name)
        
        with st.container():
            c1, c2, c3 = st.columns([1, 3, 1])
            
            with c1:
                ruta_img_A = f"Imagenes/{mapa_imagenes[fA_name]}"
                if os.path.exists(ruta_img_A): st.image(ruta_img_A, use_container_width=True)
                st.markdown(f"<p style='text-align: center; font-weight: bold; margin-bottom: 0px;'>{fA_name}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='probabilidad-under-name-small'>({pA_raw*100:.1f}% DE GANAR)</p>", unsafe_allow_html=True)
                st.markdown(renderizar_racha(fA['last_5']), unsafe_allow_html=True)
                st.markdown(f"<p class='stats-micro'>Récord: {fA['wins']}-{fA['losses']} | SLpM: {fA['slpm']} | SApM: {fA['sapm']}</p>", unsafe_allow_html=True)
                
            with c2:
                st.markdown(f"<div class='ganador-texto'>🏆 PREDICCIÓN: {ganador} ({p_win*100:.1f}%)</div>", unsafe_allow_html=True)
                with st.expander("VER DETALLES DE FINALIZACIÓN, GRÁFICA Y ANÁLISIS"):
                    col_bars, col_text = st.columns([1, 2])
                    with col_bars:
                        st.markdown(f"<p class='porcentaje-label'>KO/TKO: {p_ko*100:.1f}%</p>", unsafe_allow_html=True)
                        st.progress(int(p_ko * 100))
                        st.markdown(f"<p class='porcentaje-label'>Sumisión: {p_sub*100:.1f}%</p>", unsafe_allow_html=True)
                        st.progress(int(p_sub * 100))
                        st.markdown(f"<p class='porcentaje-label'>Decisión: {p_dec*100:.1f}%</p>", unsafe_allow_html=True)
                        st.progress(int(p_dec * 100))
                    with col_text:
                        st.markdown(f"<div class='analisis-caja'>{analisis}</div>", unsafe_allow_html=True)
                    
                    st.plotly_chart(graficar_striking(fA_name, fB_name, fA, fB), use_container_width=True)

            with c3:
                ruta_img_B = f"Imagenes/{mapa_imagenes[fB_name]}"
                if os.path.exists(ruta_img_B): st.image(ruta_img_B, use_container_width=True)
                st.markdown(f"<p style='text-align: center; font-weight: bold; margin-bottom: 0px;'>{fB_name}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='probabilidad-under-name-small'>({pB_raw*100:.1f}% DE GANAR)</p>", unsafe_allow_html=True)
                st.markdown(renderizar_racha(fB['last_5']), unsafe_allow_html=True)
                st.markdown(f"<p class='stats-micro'>Récord: {fB['wins']}-{fB['losses']} | SLpM: {fB['slpm']} | SApM: {fB['sapm']}</p>", unsafe_allow_html=True)
        st.markdown("---")

# 
# MODO 2: ANÁLISIS INDIVIDUAL PROFUNDO

else:
    pelea_seleccionada = st.sidebar.selectbox("Filtra el Combate:", [f"{a} vs {b}" for a, b in cartelera])
    fA_name, fB_name = pelea_seleccionada.split(" vs ")
    ganador, p_win, p_ko, p_sub, p_dec, analisis, pA_raw, pB_raw, fA, fB = calcular_combate(fA_name, fB_name)

    # 👇 Aquí cambiamos la proporción a [1, 2, 1] para que las imágenes laterales se vean más pequeñas y elegantes
    col1, col_vs, col2 = st.columns([1, 2, 1])

    with col1:
        ruta_img_A = f"Imagenes/{mapa_imagenes[fA_name]}"
        if os.path.exists(ruta_img_A): st.image(ruta_img_A, use_container_width=True)
        st.markdown(f"<h3 style='text-align: center;'>{fA_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p class='probabilidad-under-name'>({pA_raw*100:.1f}% DE GANAR)</p>", unsafe_allow_html=True)
        st.markdown(renderizar_racha(fA['last_5']), unsafe_allow_html=True)
        st.metric("Récord", f"{fA['wins']}-{fA['losses']}")
        st.metric("Golpes / Min (SLpM)", fA['slpm'])
        st.metric("Daño Absorbido (SApM)", fA['sapm'])

    with col_vs:
        st.markdown("<br><br><h1 style='text-align: center; font-size: 70px; color: #444;'>VS</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='ganador-texto'>🏆 {ganador}<br>({p_win*100:.1f}%)</div>", unsafe_allow_html=True)
        
        st.markdown(f"<p class='porcentaje-label'>Prob. KO/TKO: {p_ko*100:.1f}%</p>", unsafe_allow_html=True)
        st.progress(int(p_ko * 100))
        st.markdown(f"<p class='porcentaje-label'>Prob. Sumisión: {p_sub*100:.1f}%</p>", unsafe_allow_html=True)
        st.progress(int(p_sub * 100))
        st.markdown(f"<p class='porcentaje-label'>Prob. Decisión: {p_dec*100:.1f}%</p>", unsafe_allow_html=True)
        st.progress(int(p_dec * 100))

    with col2:
        # 👇 Aquí estaba el error. Ya tiene la "I" mayúscula en Imagenes/
        ruta_img_B = f"Imagenes/{mapa_imagenes[fB_name]}"
        if os.path.exists(ruta_img_B): st.image(ruta_img_B, use_container_width=True)
        st.markdown(f"<h3 style='text-align: center;'>{fB_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p class='probabilidad-under-name'>({pB_raw*100:.1f}% DE GANAR)</p>", unsafe_allow_html=True)
        st.markdown(renderizar_racha(fB['last_5']), unsafe_allow_html=True)
        st.metric("Récord", f"{fB['wins']}-{fB['losses']}")
        st.metric("Golpes / Min (SLpM)", fB['slpm'])
        st.metric("Daño Absorbido (SApM)", fB['sapm'])

    st.plotly_chart(graficar_striking(fA_name, fB_name, fA, fB), use_container_width=True)
    st.markdown("### 🧠 ANÁLISIS DEL MOTOR HEURÍSTICO")
    st.markdown(f"<div class='analisis-caja'>{analisis}</div>", unsafe_allow_html=True)
    st.markdown("---")


# PÓSTER OFICIAL AL FINAL
# 
ruta_poster = "Imagenes/UFC_CASA BLANCA.jpg"
st.markdown("<br><h2 style='text-align: center;'>CARTELERA OFICIAL</h2>", unsafe_allow_html=True)
if os.path.exists(ruta_poster):
    poster_col_1, poster_col_2, poster_col_3 = st.columns([1, 2, 1])
    with poster_col_2:
        st.image(ruta_poster, use_container_width=True)
else:
    st.warning(f"Sube la imagen '{ruta_poster}' a tu carpeta para ver el póster aquí.")
    
    
    # 
# DISCLAIMER LEGAL / AVISO DEL SISTEMA
# 
st.markdown("""
    <div style='background-color: #0A0A0C; padding: 20px; border-radius: 5px; border: 1px solid #333333; margin-top: 50px; text-align: center; box-shadow: inset 0 0 10px #000000;'>
        <p style='color: #777777; font-size: 13px; font-family: "Courier New", Courier, monospace; line-height: 1.5; margin: 0;'>
            <strong style='color: #D20000;'>⚠️ AVISO DEL ORÁCULO:</strong> Las proyecciones mostradas en este dashboard son generadas por un modelo heurístico fundamentado estrictamente en el cruce de estadísticas históricas oficiales (Striking, Grappling, Daño Absorbido y Momentum). Sin embargo, el octágono es impredecible y las matemáticas no pueden medir el corazón de un peleador. Este análisis tiene fines netamente educativos, analíticos y de entretenimiento. No representa una garantía absoluta del 100% ni constituye consejo financiero o de apuestas deportivas. ¡Disfruten de la cartelera!
        </p>
    </div>
""", unsafe_allow_html=True)
