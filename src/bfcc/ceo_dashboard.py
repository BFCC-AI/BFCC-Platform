.from decision_center import DecisionCenter
from ai_mission_control import AIMissionControl
from opportunity_bank import OpportunityBank
from portfolio_analyzer import PortfolioAnalyzer
from capital_rotation import CapitalRotationManager


class CEODashboard:
    def __init__(self):
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
            "name": "CEO Dashboard",
            "version": "1.0",
            "status": self.status,
            "decision_center": self.decision_center,
            "ai_mission_control": self.ai_mission_control,
            "opportunity_bank": self.opportunity_bank,
            "portfolio_analyzer": self.portfolio_analyzer,
            "capital_rotation": self.capital_rotation,
        }