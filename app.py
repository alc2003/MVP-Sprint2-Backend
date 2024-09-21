from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
import random, requests
from sqlalchemy.exc import IntegrityError
from model import Session, Paciente, Atendimento, cep
from logger import logger
from schemas import *
from flask_cors import CORS
from flask import jsonify



info = Info(title="Terminal de triagem", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

if __name__ == "__main__":
    app.run(debug=True)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
paciente_tag = Tag(name="Paciente", description="Adição, visualização e remoção de pacientes à base")
atendimento_tag = Tag(name="Atendimento", description="Adição, vizualização de um atendimento à um paciente cadastrado na base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.get('/consulta_cep/<cep>', tags=[paciente_tag], responses={"200": CepSchema, "400": ErrorSchema})
def consulta_cep(cep: str):
    """Consulta o endereço com base no CEP informado usando a API ViaCEP."""
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        data = response.json()

        if "erro" in data:
            return jsonify({"message": "CEP não encontrado"}), 400

        # Retorna a resposta mapeada pelo modelo ViaCEPResponse
        return jsonify(CepSchema(ViaCEPResponse(**data)).dict()), 200

    except Exception as e:
        return jsonify({"message": "Erro ao consultar o CEP"}), 400
    

@app.post('/adiciona_paciente', tags=[paciente_tag],
          responses={"200":  PacienteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_paciente(form: PacienteSchema):
    """Adiciona um novo Paciente à base de dados
    Retorna uma representação dos pacientes e atendimentos associados.
    """
    #logger.warning("teste", form)
    paciente = Paciente(
        #id=form.id,
        cns = form.cns,
        nome = form.nome,  
        sexo = form.sexo,
        telefone = form.telefone,
        cep = form.cep)
    
    logger.debug(f"Adicionando paciente de nome: '{paciente.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        logger.warning("start add: %s", paciente);
        # adicionando paciente
        session.add(paciente)
        logger.warning("end add: %s", paciente)
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado paciente de nome: '{paciente.nome}'")
        return apresenta_paciente(paciente), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Paciente de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar paciente '{paciente.nome}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo paciente :/"
        logger.warning(f"Erro ao adicionar paciente '{paciente.nome}', {error_msg}")
        return {"mesage": error_msg}, 400
    
@app.get('/busca_pacientes', tags=[paciente_tag],
         responses={"200": ListagemPacienteSchema, "404": ErrorSchema})
def get_pacientes():
    """Faz a busca por todos os Pacientes cadastrados

    Retorna uma representação da listagem de pacientes.
    """
    logger.debug(f"Coletando pacientes ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    pacientes = session.query(Paciente).all()

    if not pacientes:
        # se não há pacientes cadastrados
        return {"pacientes": []}, 200
    else:
        logger.debug(f"%d pacientes econtrados" % len(pacientes))
        # retorna as informações do paciente
        print(pacientes)
        return apresenta_pacientes(pacientes), 200    
    
@app.post('/alterar_paciente', tags=[paciente_tag],
          responses={"200": PacienteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def alterar_paciente(form: PacienteSchema):
    """Altera os dados de um Paciente na base de dados
    """
    paciente_id = form.id
    logger.warning(form)
    print(paciente_id)
    logger.debug(f"alterando dados sobre paciente #{paciente_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a alteração
    #count = session.query(Paciente).filter(Paciente.id == paciente_id).update({"nome": form.nome,"cns": form.cns,"telefone": form.telefone})

    paciente = session.query(Paciente).filter(Paciente.id == paciente_id).one_or_none()
    if paciente:
        # Atualiza os dados do paciente
        paciente.nome = form.nome
        paciente.cns = form.cns
        paciente.telefone = form.telefone
        paciente.cep = form.cep

        # Confirma a transação
        session.commit()
        print("Paciente atualizado com sucesso.")
    else:
        print(f"Paciente com ID {paciente_id} não encontrado.")

    #session.commit()

    if paciente:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"alterado paciente #{paciente_id}")
        return {"mesage": "Paciente alterado", "id": paciente_id}
    else:
        # se o paciente não foi encontrado
        error_msg = "Paciente não encontrado na base :/"
        logger.warning(f"Erro ao alterar paciente #'{paciente_id}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.get('/busca_paciente_id', tags=[paciente_tag],
         responses={"200": PacienteViewSchema, "404": ErrorSchema})
def get_paciente(query: PacienteBuscaSchema):
    """Faz a busca por um Paciente a partir do id do paciente

    Retorna uma representação dos pacientes.
    """
    paciente_id = query.id
    logger.debug(f"Coletando dados sobre paciente #{paciente_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    paciente = session.query(Paciente).filter(Paciente.id == paciente_id).first()

    if not paciente:
        # se o paciente não foi encontrado
        error_msg = "paciente não encontrado na base :/"
        logger.warning(f"Erro ao buscar paciente '{paciente_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Paciente econtrado: '{paciente.nome}'")
        # retorna a representação de paciente
        return apresenta_paciente(paciente), 200


@app.delete('/remove_paciente', tags=[paciente_tag],
            responses={"200": PacienteDelSchema, "404": ErrorSchema})
def del_paciente(query: PacienteBuscaSchema):
    """Deleta um Paciente a partir do nome de paciente informado

    Retorna uma mensagem de confirmação da remoção.
    """
    paciente_id = query.id
    print(paciente_id)
    logger.debug(f"Deletando dados sobre paciente #{paciente_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Paciente).filter(Paciente.id == paciente_id).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado paciente #{paciente_id}")
        return {"mesage": "Paciente removido", "id": paciente_id}
    else:
        # se o paciente não foi encontrado
        error_msg = "Paciente não encontrado na base :/"
        logger.warning(f"Erro ao deletar paciente #'{paciente_id}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.post('/adiciona_atendimento', tags=[atendimento_tag],
          responses={"200": PacienteViewSchema, "404": ErrorSchema})
def add_atendimento(form: AtendimentoSchema):
    """Adiciona de um novo atendimento à um pacientes cadastrado na base identificado pelo id

    Retorna uma representação dos pacientes e atendimentos associados.
    """
    paciente_id  = form.id_paciente
    logger.debug(f"Adicionando atendimentos ao paciente #{paciente_id}")
    try:
        # criando conexão com a base
        session = Session()
        # fazendo a busca pelo paciente
        paciente = session.query(Paciente).filter(Paciente.id == paciente_id).first()
        if not paciente:
            # se paciente não encontrado
            error_msg = "Paciente não encontrado na base :/"
            logger.warning(f"Erro ao adicionar atendimentos ao paciente '{paciente_id}', {error_msg}")
            return {"mesage": error_msg}, 404
        
        # criando o atendimento  
        atendimento = Atendimento(
            id_paciente= form.id_paciente,        
            hda_cod_queixa_principal = form.hda_cod_queixa_principal, 
            hda_queixa_principal = form.hda_queixa_principal, 
            hpr_hipertensao = form.hpr_hipertensao, 
            hpr_diabetes = form.hpr_diabetes, 
            hpr_cancer =  form.hpr_cancer, 
            classificacao = random.randint(1,10)
            )       

        # adicionando o atendiemnto ao paciente
        paciente.adiciona_atendimento(atendimento)
        session.commit()
        logger.debug(f"Adicionado atendimento ao paciente #{paciente_id}")
        # retorna a representação de paciente
        return apresenta_atendimento(paciente,atendimento), 200
    
    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Paciente já está na fila de atendimento :/"
        logger.warning(f"Erro ao adicionar atendimento ao paciente '{paciente_id}', {error_msg}")
        return {"mesage": error_msg}, 409


    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo paciente :/"
        logger.warning(f"Erro ao adicionar atendimento ao paciente '{paciente_id}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.delete('/remove_atendimento', tags=[atendimento_tag],
            responses={"200": AtendimentoDelSchema, "404": ErrorSchema})
def del_atendimento(query: AtendimentoBuscaSchema):
    """Deleta um Atendimento a partir do id de atendimento informado
    Retorna uma mensagem de confirmação da remoção.
    """
    atendimento_id = query.id
    print(atendimento_id)
    logger.debug(f"Deletando dados do atendimento #{atendimento_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Atendimento).filter(Atendimento.id == atendimento_id).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado atendimento #{atendimento_id}")
        return {"mesage": "Atendimento removido", "id": atendimento_id}
    else:
        # se o atendimento não foi encontrado
        error_msg = "Atendimento não encontrado na base :/"
        logger.warning(f"Erro ao deletar atendimento #'{atendimento_id}', {error_msg}")
        return {"mesage": error_msg}, 404



@app.get('/busca_atendimentos', tags=[atendimento_tag],
         responses={"200": ListagemAtendimentosSchema, "404": ErrorSchema})
def get_atendimentos():
    """Faz a busca por todos os Atendimentos cadastrados
    Retorna uma listagem de todos atendimentos.
    """
    logger.debug(f"Coletando atendimentos ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    # Consulta para obter os atendimentos ordenados por classificação
    atendimentos = session.query(Atendimento, Paciente)\
    .join(Paciente, Atendimento.id_paciente == Paciente.id)\
    .order_by(Atendimento.classificacao)\
    .all()

    result = []

    for atendimento, paciente in atendimentos:                
        result.append({
            "id": atendimento.id,
            "id_paciente": paciente.id,
            "nome": paciente.nome,
            "cns": paciente.cns,
            "hda_cod_queixa_principal": atendimento.hda_cod_queixa_principal,
            "classificacao": atendimento.classificacao

        })

    if not atendimentos:
        # se não há atendimentos cadastrados
        return {"atendimentos": []}, 200
    else:
        return result, 200
    