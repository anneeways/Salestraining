# Create a working app.py file
app_py_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sales-Training ROI Kalkulator
Workshop-Version für schnelle Entscheidungen
"""

import os
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

# Skip interactive input for testing
USE_DEFAULTS = True  # Set to False for interactive mode

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
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
        print("\\n📋 DAS SZENARIO: Joey unterstützt den Vertriebsdirektor\\n")
        print("📌 AUSGANGSSITUATION:")
        print("   • Sales-Team stagniert bei 15% Abschlussquote")
        print("   • Neue bewährte Methodik verspricht 25% Abschlussquote")
        print("   • Training übersteigt genehmigtes Trainingsbudget")
        print("\\n⚡ HERAUSFORDERUNG:")
        print("   • CFO und CEO müssen für Budgetfreigabe gewonnen werden")
        print("   • ⏰ ZEITDRUCK: Training soll in Q2 starten (6 Wochen!)")
        print("   • 🏆 WETTBEWERB: Konkurrent hat bereits 30% Steigerung erzielt")
        print("\\n🎯 JOEY'S AUFGABE:")
        print("   • Wasserdichte ROI-Argumentation erstellen")
        print("   • Budgetüberschreitung mit Zahlen rechtfertigen")
        print("=" * 80)
    
    def get_parameters_input(self) -> TrainingParameters:
        """Sammle Parameter vom Benutzer"""
        if USE_DEFAULTS:
            print("\\n📊 VERWENDE STANDARD-PARAMETER:")
            print("-" * 40)
            print("Anzahl Teilnehmer: 8")
            print("Trainingskosten pro Person: 3.000 €")
            print("Monatliche Leads: 150")
            print("Aktuelle Abschlussquote: 12%")
            print("Ziel-Abschlussquote: 20%")
            print("Durchschnittlicher Deal-Wert: 12.000 €")
            print("Marge pro Deal: 25%")
            
            return TrainingParameters(
                participants=8,
                cost_per_person=3000,
                monthly_leads=150,
                current_close_rate=12,
                target_close_rate=20,
                deal_value=12000,
                margin_rate=25
            )
        
        print("\\n📊 PARAMETER EINGEBEN:")
        print("-" * 40)
        
        def safe_input(prompt: str, default_value, input_type=int):
            """Sichere Eingabe mit Fallback"""
            try:
                user_input = input(f"{prompt} (Standard: {default_value}): ").strip()
                if not user_input:
                    return default_value
                return input_type(user_input)
            except (ValueError, KeyboardInterrupt):
                print(f"\\n⚠️ Verwende Standardwert: {default_value}")
                return default_value
        
        try:
            participants = safe_input("Anzahl Teilnehmer", 8, int)
            cost_per_person = safe_input("Trainingskosten pro Person €", 3000, float)
            monthly_leads = safe_input("Monatliche Leads Anzahl", 150, int)
            current_rate = safe_input("Aktuelle Abschlussquote %", 12, float)
            target_rate = safe_input("Ziel-Abschlussquote %", 20, float)
            deal_value = safe_input("Durchschnittlicher Deal-Wert €", 12000, float)
            margin_rate = safe_input("Marge pro Deal %", 25, float)
            
            return TrainingParameters(
                participants=participants,
                cost_per_person=cost_per_person,
                monthly_leads=monthly_leads,
                current_close_rate=current_rate,
                target_close_rate=target_rate,
                deal_value=deal_value,
                margin_rate=margin_rate
            )
        except Exception as e:
            print(f"\\n❌ Fehler bei Eingabe: {e}")
            print("Verwende Beispiel-Werte.")
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
        
        print("\\n" + "=" * 80)
        print("💰 ERGEBNISSE DER ROI-BERECHNUNG")
        print("=" * 80)
        
        # Kern-Metriken
        print(f"\\n🎯 KERN-METRIKEN:")
        print(f"   💸 Gesamtinvestition:      {self.format_currency(r.total_investment)}")
        print(f"   📈 Mehrumsatz/Monat:       {self.format_currency(r.monthly_revenue)}")
        print(f"   💰 Zusatzgewinn/Monat:     {self.format_currency(r.monthly_margin)}")
        print(f"   🚀 ROI (12 Monate):        {r.roi_percentage:.0f}%")
        print(f"   ⚡ Payback-Zeit:           {r.payback_days} Tage")
        print(f"   🎖️  Zusätzlicher Jahresgewinn: {self.format_currency(r.annual_margin)}")
        
        # Berechnungsdetails
        print(f"\\n🔢 BERECHNUNGSDETAILS:")
        print(f"   1️⃣  Training: {self.parameters.participants} × {self.format_currency(self.parameters.cost_per_person)} = {self.format_currency(r.training_costs)}")
        print(f"   2️⃣  Ausfallzeit: {self.parameters.participants} × 3 Tage × 400€ = {self.format_currency(r.opportunity_costs)}")
        print(f"   3️⃣  Vorher: {self.parameters.monthly_leads} × {self.parameters.current_close_rate}% = {r.current_deals:.1f} Deals/Monat")
        print(f"   4️⃣  Nachher: {self.parameters.monthly_leads} × {self.parameters.target_close_rate}% = {r.target_deals:.1f} Deals/Monat")
        print(f"   5️⃣  Zusätzlich: {r.additional_deals:.1f} Deals/Monat")
        print(f"   6️⃣  Marge: {self.format_currency(r.monthly_revenue)} × {self.parameters.margin_rate}% = {self.format_currency(r.monthly_margin)}")
        
        # Empfehlung
        print(f"\\n" + "=" * 80)
        if r.roi_percentage > 100 and r.payback_days
