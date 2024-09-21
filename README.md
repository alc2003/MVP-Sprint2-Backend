# Meu MVP - Terminal de triagem

Este projeto consiste em um protótipo de um terminal de cadastro de pacientes.
Para simular o cadastro dospacientes do front react.(https://github.com/alc2003/MVP-Sprint2-Frontend)


---
## Como executar 


Será necessário ter todas as libs python listadas no `requirements.txt` instaladas.
Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).
python -m venv env 
.\env\Scripts\activate  

```
(env)$ pip install -r requirements.txt
```

Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

Para executar a API  basta executar:

```
(env)$ flask run --host 0.0.0.0 --port 5000
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor
automaticamente após uma mudança no código fonte. 

```
(env)$ flask run --host 0.0.0.0 --port 5000 --reload
```

Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API em execução.

************
Para dar o build do Docker utilizando a env basta basta executar o comando
---
docker build -t my_flask_app .
----

Para rodar o Docker utilizando o ambiente env criado basta basta executar o comando
---
docker run -d -p 5000:5000 my_flask_app

