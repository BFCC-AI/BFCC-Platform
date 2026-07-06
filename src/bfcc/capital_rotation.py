"""Capital Rotation Module for BFCC Platform.

This module handles intelligent capital allocation and rotation strategies
across the investment portfolio, ensuring disciplined capital deployment
aligned with market opportunities and risk parameters.

Core Responsibilities:
    - Track capital availability and deployment
    - Evaluate rotation opportunities
    - Calculate rebalancing requirements
    - Monitor capital efficiency metrics
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AllocationStrategy(Enum):
    """Capital allocation strategy types."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class RotationStatus(Enum):
    """Status of capital rotation operations."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CapitalPosition:
    """Represents a capital position in the portfolio."""

    position_id: str
    asset_class: str
    allocation_pct: float
    current_value: float
    target_value: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_variance(self) -> float:
        """Calculate variance between current and target allocation.

        Returns:
            Percentage variance. Positive indicates over-allocation.
        """
        if self.target_value is None or self.target_value == 0:
            return 0.0
        return ((self.current_value - self.target_value) / self.target_value) * 100


@dataclass
class RotationOpportunity:
    """Represents a capital rotation opportunity."""

    opportunity_id: str
    from_position: CapitalPosition
    to_position: CapitalPosition
    amount: float
    expected_return: float
    risk_score: float
    priority: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_viable(self) -> bool:
        """Check if rotation opportunity meets viability criteria.

        Returns:
            True if opportunity should be considered for execution.
        """
        return (
            self.amount > 0
            and self.risk_score <= 100
            and self.expected_return > 0
        )


class CapitalRotationManager:
    """Manages capital rotation strategies and execution.

    This class orchestrates the capital allocation and rotation process,
    ensuring alignment with portfolio targets and risk management policies.
    """

    def __init__(
        self,
        strategy: AllocationStrategy = AllocationStrategy.BALANCED,
        rebalance_threshold: float = 5.0,
    ):
        """Initialize the Capital Rotation Manager.

        Args:
            strategy: Allocation strategy to use.
            rebalance_threshold: Percentage threshold to trigger rebalancing.
        """
        self.strategy = strategy
        self.rebalance_threshold = rebalance_threshold
        self.positions: Dict[str, CapitalPosition] = {}
        self.rotation_history: List[RotationOpportunity] = []
        self.total_capital = 0.0

        logger.info(
            f"CapitalRotationManager initialized with strategy={strategy.value}"
        )

    def add_position(self, position: CapitalPosition) -> None:
        """Add a capital position to the portfolio.

        Args:
            position: Capital position to add.
        """
        self.positions[position.position_id] = position
        self.total_capital += position.current_value
        logger.debug(f"Added position: {position.position_id}")

    def remove_position(self, position_id: str) -> Optional[CapitalPosition]:
        """Remove a capital position from the portfolio.

        Args:
            position_id: ID of position to remove.

        Returns:
            The removed position, or None if not found.
        """
        position = self.positions.pop(position_id, None)
        if position:
            self.total_capital -= position.current_value
            logger.debug(f"Removed position: {position_id}")
        return position

    def identify_rotation_opportunities(
        self,
        min_expected_return: float = 2.0,
        max_risk_score: float = 75.0,
    ) -> List[RotationOpportunity]:
        """Identify potential capital rotation opportunities.

        Args:
            min_expected_return: Minimum expected return threshold (%).
            max_risk_score: Maximum acceptable risk score (0-100).

        Returns:
            List of viable rotation opportunities sorted by priority.
        """
        opportunities = []

        # Check for over-allocated positions
        overallocated = [
            p for p in self.positions.values() if p.get_variance() > self.rebalance_threshold
        ]

        # Check for underallocated positions
        underallocated = [
            p for p in self.positions.values()
            if p.get_variance() < -self.rebalance_threshold
        ]

        # Match rotation pairs
        for from_pos in overallocated:
            for to_pos in underallocated:
                rotation_amount = self._calculate_rotation_amount(
                    from_pos, to_pos
                )

                if rotation_amount > 0:
                    opportunity = RotationOpportunity(
                        opportunity_id=f"ROT_{from_pos.position_id}_{to_pos.position_id}",
                        from_position=from_pos,
                        to_position=to_pos,
                        amount=rotation_amount,
                        expected_return=min_expected_return,
                        risk_score=self._calculate_risk_score(from_pos, to_pos),
                        priority=self._calculate_priority(from_pos, to_pos),
                    )

                    if (
                        opportunity.is_viable()
                        and opportunity.risk_score <= max_risk_score
                    ):
                        opportunities.append(opportunity)

        # Sort by priority (highest first)
        opportunities.sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"Identified {len(opportunities)} rotation opportunities")

        return opportunities

    def calculate_rebalancing_actions(
        self,
    ) -> Dict[str, float]:
        """Calculate required rebalancing actions for all positions.

        Returns:
            Dictionary mapping position IDs to required adjustments (positive=add, negative=remove).
        """
        adjustments = {}

        for position_id, position in self.positions.items():
            if position.target_value is not None:
                adjustment = position.target_value - position.current_value
                if abs(adjustment) > (position.current_value * self.rebalance_threshold / 100):
                    adjustments[position_id] = adjustment
                    logger.debug(
                        f"Position {position_id} requires adjustment: {adjustment}"
                    )

        return adjustments

    def execute_rotation(self, opportunity: RotationOpportunity) -> bool:
        """Execute a capital rotation opportunity.

        Args:
            opportunity: The rotation opportunity to execute.

        Returns:
            True if execution was successful.
        """
        try:
            # Validate preconditions
            if opportunity.amount > opportunity.from_position.current_value:
                logger.warning(
                    f"Insufficient capital in {opportunity.from_position.position_id}"
                )
                return False

            # Execute rotation
            opportunity.from_position.current_value -= opportunity.amount
            opportunity.to_position.current_value += opportunity.amount

            # Record in history
            self.rotation_history.append(opportunity)
            logger.info(
                f"Executed rotation: {opportunity.opportunity_id} - Amount: {opportunity.amount}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to execute rotation: {str(e)}")
            return False

    def get_portfolio_summary(self) -> Dict:
        """Get a summary of the current portfolio state.

        Returns:
            Dictionary containing portfolio metrics and status.
        """
        total_value = sum(p.current_value for p in self.positions.values())
        allocations = {
            p.position_id: (p.current_value / total_value * 100)
            for p in self.positions.values()
            if total_value > 0
        }

        return {
            "total_capital": total_value,
            "num_positions": len(self.positions),
            "allocations": allocations,
            "strategy": self.strategy.value,
            "total_rotations": len(self.rotation_history),
        }

    def _calculate_rotation_amount(
        self, from_pos: CapitalPosition, to_pos: CapitalPosition
    ) -> float:
        """Calculate optimal rotation amount between two positions.

        Args:
            from_pos: Source position.
            to_pos: Target position.

        Returns:
            Optimal rotation amount.
        """
        excess = from_pos.current_value - (
            from_pos.target_value if from_pos.target_value else from_pos.current_value
        )
        deficit = (to_pos.target_value if to_pos.target_value else to_pos.current_value) - to_pos.current_value
        return min(max(excess, 0), max(deficit, 0))

    def _calculate_risk_score(
        self, from_pos: CapitalPosition, to_pos: CapitalPosition
    ) -> float:
        """Calculate risk score for a rotation opportunity.

        Args:
            from_pos: Source position.
            to_pos: Target position.

        Returns:
            Risk score (0-100).
        """
        # Simple implementation - can be enhanced with more sophisticated risk models
        return 50.0

    def _calculate_priority(
        self, from_pos: CapitalPosition, to_pos: CapitalPosition
    ) -> int:
        """Calculate priority for a rotation opportunity.

        Args:
            from_pos: Source position.
            to_pos: Target position.

        Returns:
            Priority score (higher = more important).
        """
        variance_score = abs(from_pos.get_variance()) + abs(to_pos.get_variance())
        return int(variance_score * 10)


def get_manager(
    strategy: AllocationStrategy = AllocationStrategy.BALANCED,
) -> CapitalRotationManager:
    """Factory function to create a Capital Rotation Manager.

    Args:
        strategy: Allocation strategy to use.

    Returns:
        Configured CapitalRotationManager instance.
    """
    return CapitalRotationManager(strategy=strategy)
