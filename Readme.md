# Nexa Clinical Software - Sistema de Gestão de Clínica

## 📌 Resumo do Projeto
O **Nexa Clinical** é um sistema de gestão de clínicas desenvolvido em **Python**, com uma arquitetura **cliente-servidor robusta**.  
Ele oferece uma **interface gráfica moderna** para a gestão completa de **pacientes, profissionais, procedimentos e agendamentos**, além de contar com um **sistema de permissões** que diferencia o acesso entre profissionais e secretariado.

O sistema foi projetado para ser **multi-clínica**, permitindo que diferentes unidades operem em seus próprios bancos de dados isolados, todos geridos por um **servidor central**.

---

## 🏗 Arquitetura do Sistema

### 🔹 Servidor (Notebook Ubuntu)
- **Base de Dados PostgreSQL**  
  - Armazena todos os dados de forma segura.  
  - Inclui um banco de dados de gestão (`gerenciador_db`) para controlar o acesso das clínicas.  
  - Cada unidade possui seu próprio banco de dados operacional (ex: `clinica_db`).  

- **API Flask (`api_clinica.py`)**  
  - Intermediário seguro entre a aplicação cliente e o banco de dados.  
  - Responsável por validar logins das clínicas e fornecer os detalhes de conexão corretos.  

### 🔹 Cliente (Aplicação Desktop)
- **Interface Gráfica (CustomTkinter)**  
  - Construída em **CustomTkinter** para uma aparência moderna e responsiva.  

- **Cliente de API (`api_client.py`)**  
  - Responsável pelas chamadas de rede para a API no servidor.  

- **Gestor de Banco de Dados (`database_manager.py`)**  
  - Após autenticação, conecta-se diretamente ao banco da clínica para realizar operações do dia a dia.  

---

## 📂 Estrutura de Diretórios

```
/
├── main.py                   # Ponto de entrada da aplicação cliente
├── api_clinica.py            # (Servidor) API Flask para gestão de logins
├── popular_db.py              # (Servidor) Script para popular os bancos
├── migracao_db.py             # Script para migrar dados do SQLite -> PostgreSQL
├── .gitignore                 # Arquivos a serem ignorados pelo Git

├── icons/                     # Ícones da interface
│   ├── home.png
│   ├── agenda.png
│   ├── pacientes.png
│   ├── procedimentos.png
│   └── profissionais.png

├── gui/                       # Interface gráfica
│   ├── main_window.py         # Janela principal
│   ├── clinic_login_window.py # Login da clínica
│   ├── login_window.py        # Login do profissional
│   ├── main_interface.py      # Layout com navegação
│   ├── __init__.py
│   ├── tabs/                  # Abas da aplicação
│   │   ├── inicio_tab.py
│   │   ├── pacientes_tab.py
│   │   ├── agenda_tab.py
│   │   ├── procedimentos_tab.py
│   │   ├── profissionais_tab.py
│   │   └── base_tab.py
│   └── dialogs/               # Janelas de diálogo
│       ├── paciente_dialog.py
│       ├── profissional_dialog.py
│       ├── procedimento_dialog.py
│       └── agendamento_dialog.py

├── database/                  # Acesso ao banco de dados
│   ├── database_manager.py
│   └── __init__.py

├── models/                    # Classes de dados
│   ├── paciente.py
│   ├── agendamento.py
│   ├── procedimento.py
│   ├── profissional.py
│   └── __init__.py

├── Images/                    # Logos
│   └── Nexa_login.jpg

└── services/                  # Lógica de negócio
    ├── auth_service.py
    └── __init__.py
```

---

## ⚙️ Tecnologias Utilizadas

- **Linguagem:** Python  
- **Interface Gráfica:** CustomTkinter, Pillow (PIL)  
- **Banco de Dados:** PostgreSQL  
- **API do Servidor:** Flask  
- **Comunicação Cliente-Servidor:** Requests  

---

## 📄 Licença
Este projeto é de uso privado e não possui licença pública definida.  
Entre em contato com o autor para informações sobre utilização.

---
💻 Desenvolvido com dedicação para gestão eficiente de clínicas.
