from datetime import date
from pydantic import BaseModel,ConfigDict,Field,model_validator

SECTIONS={"sales","inventory","margins","customers","losses","payments","forecasts"}


class ReportRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    title:str=Field(default="Informe comercial",min_length=3,max_length=160)
    sections:list[str]=Field(default_factory=lambda:["sales"],min_length=1,max_length=7)
    date_from:date|None=None
    date_to:date|None=None

    @model_validator(mode="after")
    def validate_report(self):
        unknown=set(self.sections)-SECTIONS
        if unknown:raise ValueError(f"Secciones desconocidas: {', '.join(sorted(unknown))}")
        if self.date_from and self.date_to and self.date_to<self.date_from:raise ValueError("Rango de fechas inválido")
        return self
