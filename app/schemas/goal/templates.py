from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GoalTemplateTarget(BaseModel):
    """Sub-structure for the default target stored inside defaults."""
    type: str = Field(..., description="Target type identifier (e.g., bmi, weight_lb)")
    value: Optional[float] = Field(
        None, description="Optional numeric target value (BMI, weight, etc.)"
    )


class GoalTemplatePaceMode(BaseModel):
    """Sub-structure for the pace mode stored inside defaults."""
    weekly_rate_pct_bw: float = Field(
        ..., description="Weekly weight change as percent of bodyweight"
    )


class GoalTemplateSafety(BaseModel):
    """Safety guardrails nested within defaults."""
    max_deficit_pct_tdee: Optional[float] = Field(
        None, description="Maximum allowed deficit as percent of TDEE"
    )
    max_surplus_pct_tdee: Optional[float] = Field(
        None, description="Maximum allowed surplus as percent of TDEE"
    )
    min_calories_kcal: Optional[float] = Field(
        None, description="Minimum calories boundary"
    )
    bmi_lower_bound: Optional[float] = Field(
        None, description="Lower BMI bound for cut templates"
    )
    bmi_upper_bound: Optional[float] = Field(
        None, description="Upper BMI bound for bulk templates"
    )

    class Config:
        extra = "allow"


class GoalTemplateDefaults(BaseModel):
    """Structured payload stored in GoalTemplateBase.defaults."""
    type: str = Field(..., description="Template type (cut, bulk, recomp, etc.)")
    supported_target_types: List[str] = Field(
        default_factory=list,
        description="Allowed goal target types clients may request",
    )
    default_target: GoalTemplateTarget = Field(
        ..., description="Server default target configuration"
    )
    pace_modes: Dict[str, GoalTemplatePaceMode] = Field(
        default_factory=dict,
        description="Available pace modes and their weight-change rules",
    )
    protein_rule_default: str = Field(..., description="Default protein rule identifier")
    fat_min_g_per_lb: float = Field(
        ..., description="Fat floor in grams per lb bodyweight"
    )
    macro_allocation: str = Field(
        ..., description="Macro allocation strategy identifier"
    )
    energy_method_default: str = Field(
        ..., description="Default energy-expenditure method identifier"
    )
    fallback_activity_level: str = Field(
        ..., description="Template default PAL slug when no override exists"
    )
    variants_supported: List[str] = Field(
        default_factory=list,
        description="Supported preset variant sets (e.g., rest_workout)",
    )
    default_variants_basis: str = Field(
        ..., description="Default variant basis for preset generation"
    )
    safety: GoalTemplateSafety = Field(
        default_factory=GoalTemplateSafety,
        description="Safety constraints for deficit/surplus, BMI, calories, etc.",
    )

    class Config:
        extra = "allow"


class GoalTemplateBase(BaseModel):
    """Full template row plus typed defaults payload."""
    slug: str
    version: int = Field(1, ge=1)
    name: str
    description: str
    defaults: GoalTemplateDefaults
    active: bool = True


class GoalTemplateRead(GoalTemplateBase):
    created_at: datetime

    class Config:
        from_attributes = True


class GoalTemplateListResponse(BaseModel):
    templates: List[GoalTemplateRead]
