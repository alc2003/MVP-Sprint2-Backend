
from typing import Optional, List
from model.paciente import Paciente, Atendimento
from pydantic import BaseModel

  
class CepSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no cns do paciente.
    """    
    cep: str = "79000-000"
