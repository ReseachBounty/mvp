class EnumTipoAzienda(str, Enum):
    STARTUP = "Startup"
    PMI = "PMI"
    CORPORATE = "Corporate"


class CompanyInfo:
    name: str
    url_linkedin: str
    url_sito: str
    nazione: str
    citta: str
    settore: str
    tipo_azienda: EnumTipoAzienda
    id: int
