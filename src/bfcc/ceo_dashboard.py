"""
BFCC CEO Dashboard
Version: 1.0
Python: 3.11
"""
from decision_center import DecisionCenter
from ai_mission_control import AIMissionControl
from opportunity_bank import OpportunityBank
from portfolio_analyzer import PortfolioAnalyzer
from capital_rotation import CapitalRotationManager
class CEODashboard:
    """
    Main CEO Dashboard for BFCC Platform.
    """

    def __init__(self):
        self.name = "BFCC CEO Dashboard"
        self.version = "1.0"
        self.status = "Ready"
self.decision_center = DecisionCenter()
self.ai_mission_control = AIMissionControl()
self.opportunity_bank = OpportunityBank()
self.portfolio_analyzer = PortfolioAnalyzer()
self.capital_rotation = CapitalRotationManager()

    def start(self):
        self.status = "Running"
        print("BFCC CEO Dashboard started.")

    def stop(self):
        self.status = "Stopped"
        print("BFCC CEO Dashboard stopped.")

    def get_status(self):
               return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "decision_center": self.decision_center.get_status(),
            "ai_mission_control": self.ai_mission_control.get_status(),
            "opportunity_bank": self.opportunity_bank.get_status(),
            "portfolio_analyzer": self.portfolio_analyzer.get_status(),
            "capital_rotation": self.capital_rotation.get_status(),
        }
         
        
            
            
            
