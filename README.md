# Emulador de Sistema de Arquivos Lustre

## 📖 Sobre o Projeto

Este projeto é uma aplicação web educacional desenvolvida para simular e visualizar os conceitos fundamentais do **Lustre**, um sistema de arquivos paralelo de alto desempenho. A aplicação permite que os usuários interajam com uma representação visual da arquitetura do Lustre, compreendendo na prática como funcionam a separação de metadados (MDS), o armazenamento de objetos (OSS) e a distribuição de dados (*striping*).

Este emulador foi construído como uma ferramenta de aprendizado para materializar a teoria por trás de sistemas de arquivos distribuídos.

---

## ✨ Funcionalidades Principais

* **Simulação da Arquitetura MDS/OSS:** Separação clara entre o banco de dados de metadados e o armazenamento físico dos "chunks" de dados.
* **Striping de Arquivos Configurável:** O usuário pode definir o `stripe_count` e `stripe_size` para diretórios e arquivos, simulando os comandos `lfs setstripe`.
* **Visualização Gráfica da Distribuição:** Um painel interativo mostra com barras e cores como os chunks de um arquivo são distribuídos entre os diferentes OSTs (Object Storage Targets).
* **Gerenciamento de Arquivos via Web:**
    * Upload de arquivos do computador.
    * Criação de arquivos de texto diretamente na interface.
* **Consulta de Layout:** Visualização dos metadados de layout de cada arquivo, simulando o comando `lfs getstripe`.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3
    * **Framework:** Flask
    * **Banco de Dados (MDS):** SQLite
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
* **Comunicação:** API RESTful

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e rodar o emulador em sua máquina local.

### Pré-requisitos

* [Python 3.8+](https://www.python.org/downloads/) instalado.
* Um navegador web moderno (Chrome, Firefox, etc.).

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/lustre-emulator.git](https://github.com/seu-usuario/lustre-emulator.git)
    cd lustre-emulator
    ```

2.  **Configure o Ambiente do Backend:**
    * Navegue até a pasta do backend:
        ```bash
        cd backend
        ```
    * Crie e ative um ambiente virtual:
        ```bash
        # Para Windows
        python -m venv venv
        .\venv\Scripts\activate

        # Para Mac/Linux
        python3 -m venv venv
        source venv/bin/activate
        ```
    * Instale as dependências:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Inicialize o Banco de Dados e o Armazenamento:**
    * Execute o script do banco de dados para criar a tabela inicial:
        ```bash
        python database.py
        ```
    * Crie as pastas que simulam os OSTs:
        ```bash
        # Para Windows
        mkdir storage & cd storage & mkdir ost1 ost2 ost3 ost4

        # Para Mac/Linux
        mkdir -p storage/ost1 storage/ost2 storage/ost3 storage/ost4
        ```
        (Volte para a pasta `backend` com `cd ..` depois)


4.  **Inicie o Servidor Backend:**
    * Ainda na pasta `backend` com o ambiente virtual ativado:
        ```bash
        flask run
        ```
    * O servidor estará rodando em `http://127.0.0.1:5000`. **Deixe este terminal aberto.**

5.  **Abra o Frontend:**
    * Navegue no seu explorador de arquivos até a pasta `frontend`.
    * Abra o arquivo `index.html` diretamente no seu navegador.

A aplicação estará pronta para uso!

---

## 🗺️ Roadmap de Melhorias

Este projeto tem um grande potencial para expansão. Algumas futuras funcionalidades incluem:

-   [ ] Implementar **File Level Redundancy (FLR)** com `mirror_count`.
-   [ ] Adicionar funcionalidades de **Deletar e Renomear** arquivos/diretórios.
-   [ ] Permitir a **Criação de Diretórios** pela interface.
-   [ ] Implementar **Download de Arquivos** (o endpoint do backend já existe).
-   [ ] Simular **Pools de Armazenamento**.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
