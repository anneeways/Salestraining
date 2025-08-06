#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sales-Training ROI Kalkulator
Workshop-Version für schnelle Entscheidungen

Szenario: Joey unterstützt den Vertriebsdirektor bei der Überzeugung von CFO und CEO
für ein Sales-Training, das über dem genehmigten Budget liegt.
"""

import os
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("📄 Hinweis: Für PDF-Export installieren Sie: pip install reportlab")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("📊 Hinweis: Für Grafiken installieren Sie: pip install matplotlib seaborn")


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
    
    def print_scenario(self):
        """Zeige das Szenario an"""
        print("=" * 80)
        print("🎯 SALES-TRAINING ROI KALKULATOR")
        print("=" * 80)
        print("\n📋 DAS SZENARIO: Joey unterstützt den Vertriebsdirektor\n")
        print("📌 AUSGANGSSITUATION:")
        print("   • Sales-Team stagniert bei 15% Abschlussquote")
        print("   • Neue bewährte Methodik verspricht 25% Abschlussquote")
        print("   • Training übersteigt genehmigtes Trainingsbudget")
        print("\n⚡ HERAUSFORDERUNG:")
        print("   • CFO und CEO müssen für Budgetfreigabe gewonnen werden")
        print("   • ⏰ ZEITDRUCK: Training soll in Q2 starten (6 Wochen!)")
        print("   • 🏆 WETTBEWERB: Konkurrent hat bereits 30% Steigerung erzielt")
        print("\n🎯 JOEY'S AUFGABE:")
        print("   • Wasserdichte ROI-Argumentation erstellen")
        print("   • Budgetüberschreitung mit Zahlen rechtfertigen")
        print("=" * 80)
    
    def get_parameters_input(self) -> TrainingParameters:
        """Sammle Parameter vom Benutzer"""
        print("\n📊 PARAMETER EINGEBEN:")
        print("-" * 40)
        
        try:
            participants = int(input("Anzahl Teilnehmer (z.B. 8): ") or "8")
            cost_per_person = float(input("Trainingskosten pro Person €(z.B. 3000): ") or "3000")
            monthly_leads = int(input("Monatliche Leads Anzahl (z.B. 150): ") or "150")
            current_rate = float(input("Aktuelle Abschlussquote % (z.B. 12): ") or "12")
            target_rate = float(input("Ziel-Abschlussquote % (z.B. 20): ") or "20")
            deal_value = float(input("Durchschnittlicher Deal-Wert € (z.B. 12000): ") or "12000")
            margin_rate = float(input("Marge pro Deal % (z.B. 25): ") or "25")
            
            return TrainingParameters(
                participants=participants,
                cost_per_person=cost_per_person,
                monthly_leads=monthly_leads,
                current_close_rate=current_rate,
                target_close_rate=target_rate,
                deal_value=deal_value,
                margin_rate=margin_rate
            )
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Eingabe abgebrochen oder ungültig. Verwende Beispiel-Werte.")
            return TrainingParameters(
                participants=8,
                cost_per_person=3000,
                monthly_leads=150,
                current_close_rate=12,
                target_close_rate=20,
                deal_value=12000,
                margin_rate=25
            )
    
    def print_results(self):
        """Zeige detaillierte Ergebnisse"""
        if not self.results:
            print("❌ Keine Berechnungen vorhanden!")
            return
        
        r = self.results
        
        print("\n" + "=" * 80)
        print("💰 ERGEBNISSE DER ROI-BERECHNUNG")
        print("=" * 80)
        
        # Kern-Metriken
        print(f"\n🎯 KERN-METRIKEN:")
        print(f"   💸 Gesamtinvestition:      {self.format_currency(r.total_investment)}")
        print(f"   📈 Mehrumsatz/Monat:       {self.format_currency(r.monthly_revenue)}")
        print(f"   💰 Zusatzgewinn/Monat:     {self.format_currency(r.monthly_margin)}")
        print(f"   🚀 ROI (12 Monate):        {r.roi_percentage:.0f}%")
        print(f"   ⚡ Payback-Zeit:           {r.payback_days} Tage")
        print(f"   🎖️  Zusätzlicher Jahresgewinn: {self.format_currency(r.annual_margin)}")
        
        # Berechnungsdetails
        print(f"\n🔢 BERECHNUNGSDETAILS:")
        print(f"   1️⃣  Training: {self.parameters.participants} × {self.format_currency(self.parameters.cost_per_person)} = {self.format_currency(r.training_costs)}")
        print(f"   2️⃣  Ausfallzeit: {self.parameters.participants} × 3 Tage × 400€ = {self.format_currency(r.opportunity_costs)}")
        print(f"   3️⃣  Vorher: {self.parameters.monthly_leads} × {self.parameters.current_close_rate}% = {r.current_deals:.1f} Deals/Monat")
        print(f"   4️⃣  Nachher: {self.parameters.monthly_leads} × {self.parameters.target_close_rate}% = {r.target_deals:.1f} Deals/Monat")
        print(f"   5️⃣  Zusätzlich: {r.additional_deals:.1f} Deals/Monat")
        print(f"   6️⃣  Marge: {self.format_currency(r.monthly_revenue)} × {self.parameters.margin_rate}% = {self.format_currency(r.monthly_margin)}")
        
        # Empfehlung
        print(f"\n" + "=" * 80)
        if r.roi_percentage > 100 and r.payback_days < 90:
            print("🎉 KLARE EMPFEHLUNG: TRAINING DURCHFÜHREN!")
            print("=" * 80)
            print(f"✅ ROI von {r.roi_percentage:.0f}% ist außergewöhnlich")
            print(f"✅ Payback in nur {r.payback_days} Tagen")
            print(f"✅ {self.format_currency(r.monthly_revenue)} Mehrumsatz pro Monat")
            print(f"✅ {self.format_currency(r.monthly_margin)} zusätzlicher GEWINN pro Monat")
            print(f"✅ Perfekte Argumentationsbasis für CFO und CEO!")
        elif r.roi_percentage > 50:
            print("👍 EMPFEHLUNG: TRAINING LOHNT SICH")
            print("=" * 80)
            print(f"✅ ROI von {r.roi_percentage:.0f}% rechtfertigt die Investition")
            print(f"✅ Payback-Zeit: {r.payback_days} Tage")
            print(f"✅ Monatlicher Zusatzgewinn: {self.format_currency(r.monthly_margin)}")
        else:
            print("⚠️  VORSICHT: ROI ZU NIEDRIG")
            print("=" * 80)
            print(f"❌ ROI von nur {r.roi_percentage:.0f}% rechtfertigt möglicherweise nicht die Investition")
            print(f"❌ Prüfen Sie die Parameter oder suchen Sie Alternativen")
            print(f"❌ Monatlicher Zusatzgewinn nur: {self.format_currency(r.monthly_margin)}")
    
    def run_scenario_analysis(self, scenario: str) -> str:
        """Führe Szenario-Analyse durch"""
        if not self.results:
            return "❌ Bitte zuerst eine Berechnung durchführen!"
        
        r = self.results
        
        if scenario == 'best':
            best_revenue = r.monthly_revenue * 1.3
            best_profit = best_revenue * (self.parameters.margin_rate / 100)
            best_roi = r.roi_percentage * 1.5
            return f"""
🚀 BEST CASE SZENARIO
{'='*50}
📋 Annahme: Training wirkt sogar besser als erwartet (+30% zum Ziel)

📊 Zahlen:
   • Mehrumsatz: {self.format_currency(best_revenue)}/Monat
   • Zusatzgewinn: {self.format_currency(best_profit)}/Monat  
   • ROI: ~{best_roi:.0f}%
   • Payback: ~{int(r.payback_days * 0.7)} Tage

💼 Joey's Argument:
"Selbst wenn wir konservativ rechnen, ist der ROI fantastisch. 
Im Best Case haben wir {self.format_currency(best_profit * 12)} zusätzlichen Jahresgewinn!"
            """
        
        elif scenario == 'worst':
            worst_revenue = r.monthly_revenue * 0.6
            worst_profit = worst_revenue * (self.parameters.margin_rate / 100)
            worst_roi = r.roi_percentage * 0.4
            return f"""
😟 WORST CASE SZENARIO  
{'='*50}
📋 Annahme: Training zeigt nur 60% der erwarteten Wirkung

📊 Zahlen:
   • Mehrumsatz: {self.format_currency(worst_revenue)}/Monat
   • Zusatzgewinn: {self.format_currency(worst_profit)}/Monat
   • ROI: ~{worst_roi:.0f}%
   • Payback: ~{int(r.payback_days * 1.7)} Tage

💼 Joey's Argument:
"Selbst im schlechtesten Fall generieren wir {self.format_currency(worst_profit * 12)} 
zusätzlichen Jahresgewinn. Das Risiko ist minimal!"
            """
        
        elif scenario == 'realistic':
            return f"""
🎯 REALISTISCHES SZENARIO (Ihre Eingaben)
{'='*50}
📊 Zahlen:
   • Gesamtinvestition: {self.format_currency(r.total_investment)}
   • Zusätzliche Deals: {r.additional_deals:.0f}/Monat
   • Mehrumsatz: {self.format_currency(r.monthly_revenue)}/Monat
   • Zusatzgewinn: {self.format_currency(r.monthly_margin)}/Monat (Marge: {self.parameters.margin_rate}%)
   • Jahresgewinn: {self.format_currency(r.annual_margin)}
   • ROI: {r.roi_percentage:.0f}%
   • Break-Even: {r.payback_days} Tage

🔍 Realitätscheck:
Bei {self.parameters.margin_rate}% Marge bedeutet das {self.format_currency(r.annual_margin)} 
zusätzlichen Jahresgewinn - das {r.roi_multiple:.1f}-fache der Investition!
            """
        
        elif scenario == 'arguments':
            return f"""
💼 TOP-ARGUMENTE FÜR CFO & CEO
{'='*50}
1️⃣  GEWINN-FOKUS: 
   "Training generiert {self.format_currency(r.annual_margin)} zusätzlichen 
   Jahresgewinn - das ist echtes Geld in der Kasse!"

2️⃣  SCHNELLE AMORTISATION:
   "Investment zahlt sich in {r.payback_days} Tagen zurück - 
   schneller als jede Maschine oder Software"

3️⃣  MARGE-HEBEL:
   "Jeder zusätzliche Deal bringt {self.format_currency(r.monthly_revenue/r.additional_deals * self.parameters.margin_rate/100)} 
   Gewinn - dauerhaft!"

4️⃣  WETTBEWERBSDRUCK:
   "Konkurrent nimmt uns täglich {self.format_currency(r.monthly_margin/30)} 
   Gewinn weg - jeden Monat den wir warten!"

5️⃣  SKALIERUNG:
   "Diese {self.parameters.margin_rate}% Marge wirkt auf ALLE zukünftigen 
   Sales - nicht nur auf das Training!"
            """
        
        elif scenario == 'risks':
            return f"""
⚠️  RISIKO-ANALYSE
{'='*50}
🎯 Hauptrisiken:
   • Training wirkt nicht: Selbst bei 50% Wirkung: {self.format_currency(r.annual_margin * 0.5)} Jahresgewinn
   • Marge sinkt: Auch bei nur {self.parameters.margin_rate-5}% Marge: {self.format_currency(r.monthly_revenue * (self.parameters.margin_rate-5)/100 * 12)} Jahresgewinn  
   • Markt verschlechtert sich: Training hilft gerade dann!

❗ GRÖßTES RISIKO: Status Quo!
   Entgangener Jahresgewinn: {self.format_currency(r.annual_margin)}

💡 Joey's Fazit:
"Jeder Tag Verzögerung kostet uns {self.format_currency(r.monthly_margin/30)} Gewinn!"
            """
        
        elif scenario == 'margin':
            margin_impact = r.monthly_revenue * 0.05
            return f"""
💰 MARGE-FOKUS: DER WAHRE HEBEL!
{'='*50}
🎯 Warum Marge entscheidend ist:

📊 Aktuelle Situation:
   {self.format_currency(r.monthly_revenue)} Mehrumsatz × {self.parameters.margin_rate}% 
   = {self.format_currency(r.monthly_margin)} Gewinn

📈 Marge-Sensitivität:
   Nur 5% mehr Marge bedeutet {self.format_currency(margin_impact)} mehr Gewinn/Monat!

📅 Langzeit-Impact:
   {self.parameters.margin_rate}% Marge über 5 Jahre = {self.format_currency(r.monthly_margin * 60)} Zusatzgewinn

💼 CFO-Argument:
"Training verbessert nicht nur Abschlussquote, sondern auch 
Verhandlungsskills → höhere Margen pro Deal!"

🎯 Bottom Line:
{self.format_currency(r.total_investment)} investieren für {self.format_currency(r.annual_margin)} Jahresgewinn 
= {(r.annual_margin/r.total_investment-1)*100:.0f}% reine Gewinnsteigerung!
            """
        
        return "❌ Unbekanntes Szenario"
    
    def interactive_menu(self):
        """Interaktives Menü für Szenario-Analysen"""
        while True:
            print(f"\n{'='*60}")
            print("🤖 AI SZENARIO-ASSISTENT FÜR JOEY'S BUSINESS CASE")
            print("=" * 60)
            print("1️⃣  🚀 Best Case Szenario")
            print("2️⃣  😟 Worst Case Szenario") 
            print("3️⃣  🎯 Realistisches Szenario")
            print("4️⃣  💼 Argumente für CFO")
            print("5️⃣  ⚠️  Risiko-Analyse")
            print("6️⃣  💰 Marge-Fokus")
            print("7️⃣  📄 Export-Funktionen")
            print("0️⃣  ❌ Beenden")
            print("-" * 60)
            
            try:
                choice = input("Wählen Sie eine Option (0-7): ").strip()
                
                if choice == '0':
                    print("👋 Auf Wiedersehen!")
                    break
                elif choice == '1':
                    print(self.run_scenario_analysis('best'))
                elif choice == '2':
                    print(self.run_scenario_analysis('worst'))
                elif choice == '3':
                    print(self.run_scenario_analysis('realistic'))
                elif choice == '4':
                    print(self.run_scenario_analysis('arguments'))
                elif choice == '5':
                    print(self.run_scenario_analysis('risks'))
                elif choice == '6':
                    print(self.run_scenario_analysis('margin'))
                elif choice == '7':
                    self.export_menu()
                else:
                    print("❌ Ungültige Eingabe. Bitte wählen Sie 0-7.")
                    
                input("\n📱 Drücken Sie Enter um fortzufahren...")
                
            except KeyboardInterrupt:
                print("\n👋 Auf Wiedersehen!")
                break
    
    def export_menu(self):
        """Export-Menü"""
        print(f"\n{'='*60}")
        print("📄 EXPORT FÜR PRÄSENTATION")
        print("=" * 60)
        print("1️⃣  📄 PDF Export")
        print("2️⃣  📊 PowerPoint Export (Text)")
        print("3️⃣  💾 JSON Export")
        print("4️⃣  📈 Grafik erstellen" + (" (verfügbar)" if HAS_MATPLOTLIB else " (nicht verfügbar)"))
        print("0️⃣  🔙 Zurück")
        print("-" * 60)
        
        choice = input("Wählen Sie eine Export-Option (0-4): ").strip()
        
        if choice == '1':
            self.export_pdf()
        elif choice == '2':
            self.export_powerpoint()
        elif choice == '3':
            self.export_json()
        elif choice == '4' and HAS_MATPLOTLIB:
            self.create_charts()
        elif choice == '4' and not HAS_MATPLOTLIB:
            print("❌ Matplotlib nicht installiert. Installieren Sie: pip install matplotlib seaborn")
        elif choice == '0':
            return
        else:
            print("❌ Ungültige Eingabe.")
    
    def export_pdf(self):
        """Export als PDF (einfache Text-Version)"""
        if not self.results:
            print("❌ Keine Berechnungen vorhanden!")
            return
        
        filename = f"Sales_Training_ROI_Analyse_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("SALES-TRAINING ROI ANALYSE\n")
            f.write("=" * 80 + "\n")
            f.write(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
            
            f.write("DAS SZENARIO\n")
            f.write("-" * 40 + "\n")
            f.write("Ausgangssituation: Sales-Team stagniert bei 15% Abschlussquote\n")
            f.write("Neue Methodik verspricht: 25% Abschlussquote\n")
            f.write("Herausforderung: Training übersteigt Trainingsbudget\n")
            f.write("Zeitdruck: Training soll in Q2 starten (6 Wochen)\n")
            f.write("Wettbewerb: Konkurrent hat bereits 30% Steigerung erzielt\n\n")
            
            r = self.results
            f.write("ERGEBNISSE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Gesamtinvestition: {self.format_currency(r.total_investment)}\n")
            f.write(f"Mehrumsatz/Monat: {self.format_currency(r.monthly_revenue)}\n")
            f.write(f"Zusatzgewinn/Monat: {self.format_currency(r.monthly_margin)}\n")
            f.write(f"ROI (12 Monate): {r.roi_percentage:.0f}%\n")
            f.write(f"Payback-Zeit: {r.payback_days} Tage\n")
            f.write(f"Zusätzlicher Jahresgewinn: {self.format_currency(r.annual_margin)}\n\n")
            
            f.write("EMPFEHLUNG\n")
            f.write("-" * 40 + "\n")
            if r.roi_percentage > 100:
                f.write("✅ KLARE EMPFEHLUNG: Training durchführen!\n")
                f.write(f"ROI von {r.roi_percentage:.0f}% ist außergewöhnlich\n")
            elif r.roi_percentage > 50:
                f.write("👍 Training lohnt sich\n")
            else:
                f.write("⚠️ ROI zu niedrig - Parameter prüfen\n")
            
            # Szenarien hinzufügen
            f.write("\n" + "="*80 + "\n")
            f.write("SZENARIO-ANALYSEN\n")
            f.write("="*80 + "\n")
            
            for scenario in ['best', 'worst', 'realistic', 'arguments', 'risks', 'margin']:
                f.write(f"\n{self.run_scenario_analysis(scenario)}\n")
        
        print(f"✅ Export erfolgreich: {filename}")
        print(f"📁 Dateigröße: {os.path.getsize(filename)} Bytes")
    
    def export_powerpoint(self):
        """Export für PowerPoint"""
        if not self.results:
            print("❌ Keine Berechnungen vorhanden!")
            return
        
        filename = f"Sales_Training_ROI_PowerPoint_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        r = self.results
        
        content = f"""# Sales-Training ROI Analyse

## 🎯 Das Szenario
- Sales-Team stagniert bei 15% Abschlussquote  
- Neue Methodik verspricht 25%
- Training übersteigt Jahresbudget
- CFO und CEO müssen überzeugt werden
- ⏰ Zeitdruck: Q2-Start (6 Wochen)
- 🏆 Konkurrent: bereits 30% Steigerung

## 💰 Kern-Ergebnisse
- **Gesamtinvestition:** {self.format_currency(r.total_investment)}
- **Mehrumsatz/Monat:** {self.format_currency(r.monthly_revenue)}
- **Zusatzgewinn/Monat:** {self.format_currency(r.monthly_margin)}
- **ROI (12 Monate):** {r.roi_percentage:.0f}%
- **Payback-Zeit:** {r.payback_days} Tage
- **Jahresgewinn:** {self.format_currency(r.annual_margin)}

## 🚀 Empfehlung
{"✅ KLARE EMPFEHLUNG: Training durchführen!" if r.roi_percentage > 100 else "👍 Training lohnt sich" if r.roi_percentage > 50 else "⚠️ ROI zu niedrig"}

## 💼 Argumente für Management
1. ROI von {r.roi_percentage:.0f}% ist außergewöhnlich
2. Payback in nur {r.payback_days} Tagen
3. {self.format_currency(r.annual_margin)} zusätzlicher Jahresgewinn  
4. Wettbewerbsvorteil gegenüber Konkurrenz
5. Einmalige Investition - dauerhafter Nutzen

## 📊 Berechnungsgrundlage
- Investment: Training + Ausfallzeiten = {self.format_currency(r.total_investment)}
- Zusätzliche Deals: {r.additional_deals:.1f}/Monat
- Marge: {self.format_currency(r.monthly_revenue)} × {self.parameters.margin_rate}% = {self.format_currency(r.monthly_margin)}
- ROI: {self.format_currency(r.annual_margin)} ÷ {self.format_currency(r.total_investment)} = {r.roi_percentage:.0f}%

---
*Erstellt mit Sales-Training ROI Kalkulator*
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ PowerPoint Export erfolgreich: {filename}")
        print("💡 Anleitung:")
        print("   1. Textdatei öffnen und Inhalt kopieren")
        print("   2. In PowerPoint einfügen")
        print("   3. Gliederungsansicht nutzen für automatische Folien")
        print("   4. Formatierung nach Bedarf anpassen")
    
    def export_json(self):
        """Export als JSON für weitere Verarbeitung"""
        if not self.results:
            print("❌ Keine Berechnungen vorhanden!")
            return
        
        filename = f"Sales_Training_ROI_Data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "scenario": "Joey unterstützt Vertriebsdirektor für Sales-Training Budget-Genehmigung",
            "parameters": {
                "participants": self.parameters.participants,
                "cost_per_person": self.parameters.cost_per_person,
                "monthly_leads": self.parameters.monthly_leads,
                "current_close_rate": self.parameters.current_close_rate,
                "target_close_rate": self.parameters.target_close_rate,
                "deal_value": self.parameters.deal_value,
                "margin_rate": self.parameters.margin_rate,
                "training_days": self.parameters.training_days,
                "daily_rate": self.parameters.daily_rate
            },
            "results": {
                "total_investment": self.results.total_investment,
                "training_costs": self.results.training_costs,
                "opportunity_costs": self.results.opportunity_costs,
                "monthly_revenue": self.results.monthly_revenue,
                "monthly_margin": self.results.monthly_margin,
                "annual_margin": self.results.annual_margin,
                "roi_percentage": self.results.roi_percentage,
                "payback_days": self.results.payback_days,
                "additional_deals_per_month": self.results.additional_deals,
                "net_benefit": self.results.net_benefit
            },
            "recommendation": "DURCHFÜHREN" if self.results.roi_percentage > 100 else "PRÜFEN" if self.results.roi_percentage > 50 else "ABLEHNEN"
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON Export erfolgreich: {filename}")
        print("💻 Verwendung: Laden Sie die Datei in Excel, Power BI oder andere Tools")
    
    def create_charts(self):
        """Erstelle Visualisierungen"""
        if not HAS_MATPLOTLIB:
            print("❌ Matplotlib nicht verfügbar!")
            return
        
        if not self.results:
            print("❌ Keine Berechnungen vorhanden!")
            return
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Sales-Training ROI Analyse - Joey\'s Business Case', fontsize=16, fontweight='bold')
        
        r = self.results
        
        # 1. Investment vs. Jahresgewinn
        categories = ['Investment', 'Jahresgewinn']
        values = [r.total_investment, r.annual_margin]
        colors = ['#e74c3c', '#27ae60']
        
        bars1 = ax1.bar(categories, values, color=colors, alpha=0.7)
        ax1.set_title('Investment vs. Jahresgewinn', fontweight='bold')
        ax1.set_ylabel('Euro (€)')
        
        # Add value labels
        for bar, value in zip(bars1, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.02, 
                    f'{value:,.0f} €', ha='center', va='bottom', fontweight='bold')
        
        # 2. Monatliche Entwicklung
        months = list(range(13))
        cumulative_benefit = []
        monthly_margin = r.monthly_margin
        
        for month in months:
            if month == 0:
                cumulative_benefit.append(-r.total_investment)
            else:
                cumulative_benefit.append(cumulative_benefit[-1] + monthly_margin)
        
        ax2.plot(months, cumulative_benefit, marker='o', linewidth=3, markersize=6, color='#3498db')
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Break-even')
        ax2.set_title('Kumulierte Gewinnentwicklung', fontweight='bold')
        ax2.set_xlabel('Monat')
        ax2.set_ylabel('Kumulierter Gewinn (€)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. ROI Sensitivitätsanalyse
        close_rates = range(int(self.parameters.target_close_rate)-5, int(self.parameters.target_close_rate)+10, 2)
        roi_values = []
        
        for rate in close_rates:
            temp_deals = self.parameters.monthly_leads * (rate/100) - r.current_deals
            temp_revenue = temp_deals * self.parameters.deal_value
            temp_margin = temp_revenue * (self.parameters.margin_rate/100) * 12
            temp_roi = ((temp_margin - r.total_investment) / r.total_investment) * 100
            roi_values.append(temp_roi)
        
        ax3.plot(close_rates, roi_values, marker='s', linewidth=3, markersize=6, color='#e67e22')
        ax3.axhline(y=100, color='orange', linestyle='--', alpha=0.7, label='100% ROI')
        ax3.axvline(x=self.parameters.target_close_rate, color='green', linestyle='--', alpha=0.7, label='Ziel-Rate')
        ax3.set_title('ROI-Sensitivität (Abschlussquote)', fontweight='bold')
        ax3.set_xlabel('Abschlussquote (%)')
        ax3.set_ylabel('ROI (%)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # 4. Vergleich: Aktuell vs. Nach Training
        scenarios = ['Aktuell', 'Nach Training']
        deals = [r.current_deals, r.target_deals]
        revenue = [r.current_deals * self.parameters.deal_value, r.target_deals * self.parameters.deal_value]
        
        x = range(len(scenarios))
        width = 0.35
        
        bars1 = ax4.bar([i - width/2 for i in x], deals, width, label='Deals/Monat', color='#3498db', alpha=0.7)
        ax4_twin = ax4.twinx()
        bars2 = ax4_twin.bar([i + width/2 for i in x], revenue, width, label='Umsatz/Monat', color='#e74c3c', alpha=0.7)
        
        ax4.set_title('Vorher vs. Nachher Vergleich', fontweight='bold')
        ax4.set_xlabel('Szenario')
        ax4.set_ylabel('Deals pro Monat', color='#3498db')
        ax4_twin.set_ylabel('Umsatz pro Monat (€)', color='#e74c3c')
        ax4.set_xticks(x)
        ax4.set_xticklabels(scenarios)
        
        # Combine legends
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.tight_layout()
        
        filename = f"Sales_Training_ROI_Charts_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        print(f"✅ Diagramme gespeichert: {filename}")
        
        # Show plot
        try:
            plt.show()
        except:
            print("💡 Diagramme wurden gespeichert, aber können nicht angezeigt werden.")


def main():
    """Hauptprogramm"""
    calculator = SalesROICalculator()
    
    # Szenario zeigen
    calculator.print_scenario()
    
    # Parameter sammeln
    parameters = calculator.get_parameters_input()
    
    # Berechnen
    print("\n🔄 Berechne ROI...")
    results = calculator.calculate_roi(parameters)
    
    # Ergebnisse zeigen
    calculator.print_results()
    
    # Interaktives Menü
    calculator.interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programm beendet. Auf Wiedersehen!")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        print("🔧 Bitte prüfen Sie Ihre Eingaben und versuchen Sie es erneut.")
