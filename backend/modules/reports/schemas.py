from datetime import date
from pydantic import BaseModel,ConfigDict,Field,model_validator

SECTIONS={"sales","inventory","margins","customers","losses","payments","forecasts"}


class ReportQuery(BaseModel):
    """Filtros comunes a los informes del catálogo, leídos de la query string.

    Cada informe declara en el catálogo cuáles admite; los que no aplique
    simplemente se ignoran, de modo que una sola ruta sirve a las dos familias.
    """
    model_config=ConfigDict(extra="ignore")
    date_from:date|None=None
    date_to:date|None=None
    search:str|None=Field(default=None,max_length=120)
    limit:int=Field(default=200,ge=1,le=1000)
    threshold:int=Field(default=10,ge=0,le=100000)
    days:int=Field(default=30,ge=1,le=365)

    @model_validator(mode="after")
    def validate_range(self):
        if self.date_from and self.date_to and self.date_to<self.date_from:raise ValueError("Rango de fechas inválido")
        return self

    @property
    def window_days(self)->int:
        """Días del periodo, usado para prorratear cobertura de inventario."""
        if self.date_from and self.date_to:return (self.date_to-self.date_from).days+1
        return self.days


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
