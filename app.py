# Create a Streamlit web app version
streamlit_app_content = '''import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import json

# Page config
st.set_page_config(
    page_title="Sales-Training ROI Kalkulator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class TrainingParameters:
    """Parameter für das Sales-Training"""
    participants: int
    cost_per_person: float
    monthly_leads: int
    current_close_rate: float
    target_close_rate: float
    deal_value: float
    margin_rate: float
    training_days: int = 3
    daily_rate: float = 400.0

@dataclass
class ROIResults:
    """Ergebnisse der ROI-Berechnung"""
    total_investment: float
    training_costs: float
    opportunity_costs: float
    current_deals: float
    target_deals: float
    additional_deals: float
    monthly_revenue: float
    monthly_margin: float
    annual_margin: float
    roi_percentage: float
    roi_multiple: float
    payback_days: int
    net_benefit: float

class SalesROICalculator:
    """Sales-Training ROI Kalkulator"""
    
    def __init__(self):
        self.parameters: Optional[TrainingParameters] = None
        self.results: Optional[ROIResults] = None
    
    def format_currency(self, amount: float) -> str:
        """Formatiere Betrag als Währung"""
        return f"{amount:,.0f} €".replace(",", ".")
    
    def calculate_roi(self, params: TrainingParameters) -> ROIResults:
        """Berechne ROI basierend auf Parametern"""
        self.parameters = params
        
        # 1. Gesamtinvestition berechnen
        training_costs = params.participants * params.cost_per_person
        opportunity_costs = params.participants * params.training_days * params.daily_rate
        total_investment = training_costs + opportunity_costs
        
        # 2. Zusätzliche Deals berechnen
        current_deals = params.monthly_leads * (params.current_close_rate / 100)
        target_deals = params.monthly_leads * (params.target_close_rate / 100)
        additional_deals = target_deals - current_deals
        
        # 3. Umsatz- und Margen-Impact
        monthly_revenue = additional_deals * params.deal_value
        monthly_margin = monthly_revenue * (params.margin_rate / 100)
        annual_margin = monthly_margin * 12
        
        # 4. ROI-Metriken
        net_benefit = annual_margin - total_investment
        roi_percentage = (net_benefit / total_investment) * 100 if total_investment > 0 else 0
        roi_multiple = net_benefit / total_investment if total_investment > 0 else 0
        payback_days = int((total_investment / monthly_margin) * 30) if monthly_margin > 0 else 0
        
        self.results = ROIResults(
            total_investment=total_investment,
            training_costs=training_costs,
            opportunity_costs=opportunity_costs,
            current_deals=current_deals,
            target_deals=target_deals,
            additional_deals=additional_deals,
            monthly_revenue=monthly_revenue,
            monthly_margin=monthly_margin,
            annual_margin=annual_margin,
            roi_percentage=roi_percentage,
            roi_multiple=roi_multiple,
            payback_days=payback_days,
            net_benefit=net_benefit
        )
        
        return self.results

def create_roi_charts(calculator):
    """Erstelle interaktive Plotly Charts"""
    if not calculator.results:
        return None
    
    r = calculator.results
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Investment vs. Jahresgewinn', 'Monatliche Gewinnentwicklung', 
                       'ROI-Sensitivität', 'Vorher vs. Nachher'),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )
    
    # 1. Investment vs Jahresgewinn
    fig.add_trace(
        go.Bar(x=['Investment', 'Jahresgewinn'], 
               y=[r.total_investment, r.annual_margin],
               marker_color=['#e74c3c', '#27ae60'],
               name='Investment vs Gewinn',
               text=[f'{r.total_investment:,.0f} €', f'{r.annual_margin:,.0f} €'],
               textposition='auto'),
        row=1, col=1
    )
    
    # 2. Monatliche Entwicklung
    months = list(range(13))
    cumulative = [-r.total_investment]
    for month in range(1, 13):
        cumulative.append(cumulative[-1] + r.monthly_margin)
    
    fig.add_trace(
        go.Scatter(x=months, y=cumulative,
                  mode='lines+markers',
                  name='Kumulierter Gewinn',
                  line=dict(color='#3498db', width=3)),
        row=1, col=2
    )
    
    # Break-even line
    fig.add_hline(y=0, line_dash="dash", line_color="red", 
                  annotation_text="Break-even", row=1, col=2)
    
    # 3. ROI Sensitivität
    close_rates = list(range(int(calculator.parameters.target_close_rate)-5, 
                            int(calculator.parameters.target_close_rate)+10, 2))
    roi_values = []
    
    for rate in close_rates:
        temp_deals = calculator.parameters.monthly_leads * (rate/100) - r.current_deals
        temp_revenue = temp_deals * calculator.parameters.deal_value
        temp_margin = temp_revenue * (calculator.parameters.margin_rate/100) * 12
        temp_roi = ((temp_margin - r.total_investment) / r.total_investment) * 100
        roi_values.append(temp_roi)
    
    fig.add_trace(
        go.Scatter(x=close_rates, y=roi_values,
                  mode='lines+markers',
                  name='ROI Sensitivität',
                  line=dict(color='#e67e22', width=3)),
        row=2, col=1
    )
    
    # 4. Vorher vs Nachher
    scenarios = ['Aktuell', 'Nach Training']
    deals = [r.current_deals, r.target_deals]
    
    fig.add_trace(
        go.Bar(x=scenarios, y=deals,
               marker_color=['#95a5a6', '#3498db'],
               name='Deals/Monat',
               text=[f'{d:.1f}' for d in deals],
               textposition='auto'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, 
                     title_text="Sales-Training ROI Analyse - Interaktive Dashboards")
    
    return fig

def main():
    """Hauptfunktion der Streamlit App"""
    
    # Header
    st.title("🎯 Sales-Training ROI Kalkulator")
    st.markdown("### Joey's Business Case für CFO & CEO")
    
    # Szenario Box
    with st.expander("📋 Das Szenario", expanded=True):
        st.markdown("""
        **Ausgangssituation:**
        - Sales-Team stagniert bei 15% Abschlussquote
        - Neue bewährte Methodik verspricht 25% Abschlussquote  
        - Training übersteigt genehmigtes Trainingsbudget
        
        **Herausforderung:**
        - CFO und CEO müssen für Budgetfreigabe gewonnen werden
        - ⏰ **ZEITDRUCK:** Training soll in Q2 starten (6 Wochen!)
        - 🏆 **WETTBEWERB:** Konkurrent hat bereits 30% Steigerung erzielt
        
        **Joey's Aufgabe:**
        - Wasserdichte ROI-Argumentation erstellen
        - Budgetüberschreitung mit Zahlen rechtfertigen
        """)
    
    # Sidebar für Parameter
    st.sidebar.header("📊 Parameter eingeben")
    
    # Parameter Input
    participants = st.sidebar.number_input("Anzahl Teilnehmer", min_value=1, max_value=50, value=8)
    cost_per_person = st.sidebar.number_input("Trainingskosten pro Person (€)", min_value=500, max_value=10000, value=3000, step=100)
    monthly_leads = st.sidebar.number_input("Monatliche Leads", min_value=10, max_value=1000, value=150, step=10)
    current_rate = st.sidebar.slider("Aktuelle Abschlussquote (%)", min_value=1.0, max_value=50.0, value=12.0, step=0.5)
    target_rate = st.sidebar.slider("Ziel-Abschlussquote (%)", min_value=1.0, max_value=50.0, value=20.0, step=0.5)
    deal_value = st.sidebar.number_input("Durchschnittlicher Deal-Wert (€)", min_value=1000, max_value=100000, value=12000, step=500)
    margin_rate = st.sidebar.slider("Marge pro Deal (%)", min_value=5.0, max_value=80.0, value=25.0, step=1.0)
    
    # Erweiterte Parameter
    with st.sidebar.expander("🔧 Erweiterte Parameter"):
        training_days = st.number_input("Trainingstage", min_value=1, max_value=10, value=3)
        daily_rate = st.number_input("Tagessatz Ausfallzeit (€)", min_value=200, max_value=1000, value=400, step=50)
    
    # Berechnung
    calculator = SalesROICalculator()
    
    params = TrainingParameters(
        participants=participants,
        cost_per_person=cost_per_person,
        monthly_leads=monthly_leads,
        current_close_rate=current_rate,
        target_close_rate=target_rate,
        deal_value=deal_value,
        margin_rate=margin_rate,
        training_days=training_days,
        daily_rate=daily_rate
    )
    
    results = calculator.calculate_roi(params)
    
    # Hauptergebnisse
    st.header("💰 Kern-Ergebnisse")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💸 Gesamtinvestition", calculator.format_currency(results.total_investment))
    
    with col2:
        st.metric("📈 Mehrumsatz/Monat", calculator.format_currency(results.monthly_revenue))
    
    with col3:
        st.metric("💰 Zusatzgewinn/Monat", calculator.format_currency(results.monthly_margin))
    
    with col4:
        st.metric("🚀 ROI (12 Monate)", f"{results.roi_percentage:.0f}%")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.metric("⚡ Payback-Zeit", f"{results.payback_days} Tage")
    
    with col6:
        st.metric("🎖️ Jahresgewinn", calculator.format_currency(results.annual_margin))
    
    # Empfehlung
    st.header("🎯 Empfehlung")
    
    if results.roi_percentage > 100 and results.payback_days < 90:
        st.success("🎉 **KLARE EMPFEHLUNG: TRAINING DURCHFÜHREN!**")
        st.markdown(f"""
        ✅ ROI von **{results.roi_percentage:.0f}%** ist außergewöhnlich  
        ✅ Payback in nur **{results.payback_days} Tagen**  
        ✅ **{calculator.format_currency(results.monthly_revenue)}** Mehrumsatz pro Monat  
        ✅ **{calculator.format_currency(results.monthly_margin)}** zusätzlicher GEWINN pro Monat  
        ✅ **Perfekte Argumentationsbasis für CFO und CEO!**
        """)
    elif results.roi_percentage > 50:
        st.warning("👍 **EMPFEHLUNG: TRAINING LOHNT SICH**")
        st.markdown(f"""
        ✅ ROI von **{results.roi_percentage:.0f}%** rechtfertigt die Investition  
        ✅ Payback-Zeit: **{results.payback_days} Tage**  
        ✅ Monatlicher Zusatzgewinn: **{calculator.format_currency(results.monthly_margin)}**
        """)
    else:
        st.error("⚠️ **VORSICHT: ROI ZU NIEDRIG**")
        st.markdown(f"""
        ❌ ROI von nur **{results.roi_percentage:.0f}%** rechtfertigt möglicherweise nicht die Investition  
        ❌ Prüfen Sie die Parameter oder suchen Sie Alternativen  
        ❌ Monatlicher Zusatzgewinn nur: **{calculator.format_currency(results.monthly_margin)}**
        """)
    
    # Charts
    st.header("📊 Interaktive Analysen")
    
    chart = create_roi_charts(calculator)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    
    # Szenario-Analysen
    st.header("🔍 Szenario-Analysen")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Best Case", "💼 CFO Argumente", "⚠️ Risiken", "💰 Marge-Fokus"])
    
    with tab1:
        best_revenue = results.monthly_revenue * 1.3
        best_profit = best_revenue * (params.margin_rate / 100)
        best_roi = results.roi_percentage * 1.5
        
        st.markdown(f"""
        ### 🚀 BEST CASE SZENARIO
        **Annahme:** Training wirkt sogar besser als erwartet (+30% zum Ziel)
        
        📊 **Zahlen:**
        - Mehrumsatz: **{calculator.format_currency(best_revenue)}/Monat**
        - Zusatzgewinn: **{calculator.format_currency(best_profit)}/Monat**
        - ROI: **~{best_roi:.0f}%**
        - Payback: **~{int(results.payback_days * 0.7)} Tage**
        
        💼 **Joey's Argument:**
        > "Selbst wenn wir konservativ rechnen, ist der ROI fantastisch. 
        > Im Best Case haben wir **{calculator.format_currency(best_profit * 12)}** zusätzlichen Jahresgewinn!"
        """)
    
    with tab2:
        st.markdown(f"""
        ### 💼 TOP-ARGUMENTE FÜR CFO & CEO
        
        **1️⃣ GEWINN-FOKUS:**
        > "Training generiert **{calculator.format_currency(results.annual_margin)}** zusätzlichen 
        > Jahresgewinn - das ist echtes Geld in der Kasse!"
        
        **2️⃣ SCHNELLE AMORTISATION:**
        > "Investment zahlt sich in **{results.payback_days} Tagen** zurück - 
        > schneller als jede Maschine oder Software"
        
        **3️⃣ MARGE-HEBEL:**
        > "Jeder zusätzliche Deal bringt **{calculator.format_currency(results.monthly_revenue/results.additional_deals * params.margin_rate/100)}** 
        > Gewinn - dauerhaft!"
        
        **4️⃣ WETTBEWERBSDRUCK:**
        > "Konkurrent nimmt uns täglich **{calculator.format_currency(results.monthly_margin/30)}** 
        > Gewinn weg - jeden Monat den wir warten!"
        
        **5️⃣ SKALIERUNG:**
        > "Diese **{params.margin_rate}%** Marge wirkt auf ALLE zukünftigen 
        > Sales - nicht nur auf das Training!"
        """)
    
    with tab3:
        st.markdown(f"""
        ### ⚠️ RISIKO-ANALYSE
        
        **🎯 Hauptrisiken:**
        - **Training wirkt nicht:** Selbst bei 50% Wirkung: **{calculator.format_currency(results.annual_margin * 0.5)}** Jahresgewinn
        - **Marge sinkt:** Auch bei nur **{params.margin_rate-5}%** Marge: **{calculator.format_currency(results.monthly_revenue * (params.margin_rate-5)/100 * 12)}** Jahresgewinn
        - **Markt verschlechtert sich:** Training hilft gerade dann!
        
        **❗ GRÖßTES RISIKO: Status Quo!**
        Entgangener Jahresgewinn: **{calculator.format_currency(results.annual_margin)}**
        
        **💡 Joey's Fazit:**
        > "Jeder Tag Verzögerung kostet uns **{calculator.format_currency(results.monthly_margin/30)}** Gewinn!"
        """)
    
    with tab4:
        margin_impact = results.monthly_revenue * 0.05
        st.markdown(f"""
        ### 💰 MARGE-FOKUS: DER WAHRE HEBEL!
        
        **🎯 Warum Marge entscheidend ist:**
        
        **📊 Aktuelle Situation:**
        {calculator.format_currency(results.monthly_revenue)} Mehrumsatz × {params.margin_rate}% 
        = **{calculator.format_currency(results.monthly_margin)}** Gewinn
        
        **📈 Marge-Sensitivität:**
        Nur 5% mehr Marge bedeutet **{calculator.format_currency(margin_impact)}** mehr Gewinn/Monat!
        
        **📅 Langzeit-Impact:**
        {params.margin_rate}% Marge über 5 Jahre = **{calculator.format_currency(results.monthly_margin * 60)}** Zusatzgewinn
        
        **💼 CFO-Argument:**
        > "Training verbessert nicht nur Abschlussquote, sondern auch 
        > Verhandlungsskills → höhere Margen pro Deal!"
        
        **🎯 Bottom Line:**
        {calculator.format_currency(results.total_investment)} investieren für {calculator.format_currency(results.annual_margin)} Jahresgewinn 
        = **{(results.annual_margin/results.total_investment-1)*100:.0f}%** reine Gewinnsteigerung!
        """)
    
    # Berechnungsdetails
    with st.expander("🔢 Berechnungsdetails anzeigen"):
        st.markdown(f"""
        **1️⃣ Training:** {params.participants} × {calculator.format_currency(params.cost_per_person)} = **{calculator.format_currency(results.training_costs)}**
        
        **2️⃣ Ausfallzeit:** {params.participants} × {params.training_days} Tage × {params.daily_rate}€ = **{calculator.format_currency(results.opportunity_costs)}**
        
        **3️⃣ Vorher:** {params.monthly_leads} × {params.current_close_rate}% = **{results.current_deals:.1f} Deals/Monat**
        
        **4️⃣ Nachher:** {params.monthly_leads} × {params.target_close_rate}% = **{results.target_deals:.1f} Deals/Monat**
        
        **5️⃣ Zusätzlich:** **{results.additional_deals:.1f} Deals/Monat**
        
        **6️⃣ Marge:** {calculator.format_currency(results.monthly_revenue)} × {params.margin_rate}% = **{calculator.format_currency(results.monthly_margin)}**
        """)
    
    # Export Funktionen
    st.header("📄 Export & Download")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON Export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "scenario": "Joey's Sales-Training ROI Analyse",
            "parameters": {
                "participants": params.participants,
                "cost_per_person": params.cost_per_person,
                "monthly_leads": params.monthly_leads,
                "current_close_rate": params.current_close_rate,
                "target_close_rate": params.target_close_rate,
                "deal_value": params.deal_value,
                "margin_rate": params.margin_rate
            },
            "results": {
                "total_investment": results.total_investment,
                "monthly_revenue": results.monthly_revenue,
                "monthly_margin": results.monthly_margin,
                "annual_margin": results.annual_margin,
                "roi_percentage": results.roi_percentage,
                "payback_days": results.payback_days
            }
        }
        
        st.download_button(
            label="📊 JSON Download",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"roi_analyse_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
    
    with col2:
        # CSV Export
        df = pd.DataFrame([{
            'Metrik': 'Gesamtinvestition',
            'Wert': results.total_investment,
            'Formatiert': calculator.format_currency(results.total_investment)
        }, {
            'Metrik': 'Monatlicher Zusatzgewinn',
            'Wert': results.monthly_margin,
            'Formatiert': calculator.format_currency(results.monthly_margin)
        }, {
            'Metrik': 'Jahresgewinn',
            'Wert': results.annual_margin,
            'Formatiert': calculator.format_currency(results.annual_margin)
        }, {
            'Metrik': 'ROI (%)',
            'Wert': results.roi_percentage,
            'Formatiert': f"{results.roi_percentage:.1f}%"
        }, {
            'Metrik': 'Payback (Tage)',
            'Wert': results.payback_days,
            'Formatiert': f"{results.payback_days} Tage"
        }])
        
        st.download_button(
            label="📈 CSV Download",
            data=df.to_csv(index=False, encoding='utf-8'),
            file_name=f"roi_ergebnisse_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    with col3:
        # PowerPoint Text Export
        ppt_content = f"""# Sales-Training ROI Analyse

## Das Szenario
- Sales-Team stagniert bei 15% Abschlussquote
- Neue Methodik verspricht 25%
- Training übersteigt Jahresbudget
- CFO und CEO müssen überzeugt werden

## Kern-Ergebnisse
- Gesamtinvestition: {calculator.format_currency(results.total_investment)}
- Mehrumsatz/Monat: {calculator.format_currency(results.monthly_revenue)}
- Zusatzgewinn/Monat: {calculator.format_currency(results.monthly_margin)}
- ROI (12 Monate): {results.roi_percentage:.0f}%
- Payback-Zeit: {results.payback_days} Tage
- Jahresgewinn: {calculator.format_currency(results.annual_margin)}

## Empfehlung
{"✅ KLARE EMPFEHLUNG: Training durchführen!" if results.roi_percentage > 100 else "👍 Training lohnt sich" if results.roi_percentage > 50 else "⚠️ ROI zu niedrig"}

## Top-Argumente für Management
1. ROI von {results.roi_percentage:.0f}% ist außergewöhnlich
2. Payback in nur {results.payback_days} Tagen
3. {calculator.format_currency(results.annual_margin)} zusätzlicher Jahresgewinn
4. Wettbewerbsvorteil gegenüber Konkurrenz
5. Einmalige Investition - dauerhafter Nutzen
"""
        
        st.download_button(
            label="📊 PowerPoint Text",
            data=ppt_content,
            file_name=f"roi_powerpoint_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
'''

# Write the Streamlit app to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(streamlit_app_content)

print("✅ Streamlit app.py wurde erfolgreich erstellt!")
print("🌐 Bereit für Online-Deployment!")
