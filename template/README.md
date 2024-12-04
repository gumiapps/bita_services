# Inventory Management Microservice

## Overview

The Inventory Management Microservice provides APIs for managing products, tracking stock levels, and inventory operations. Built using FastAPI, it ensures high performance and scalability.

---

## Features

- Create, read, update, and delete inventory items.
- Filter inventory by category or stock availability.
- API-first approach with auto-generated documentation.

---

## Table of Contents

1. [Setup](#setup)
2. [API Endpoints](#api-endpoints)
3. [Environment Variables](#environment-variables)
4. [Testing](#testing)
5. [Deployment](#deployment)
6. [Contributing](#contributing)

---

## Setup

### Prerequisites

- **Python**: 3.9+
- **Database**: PostgreSQL 12+
- **Other Tools**: Docker (optional for containerization)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/gumiapps/bita_services.git
   cd bita_services/template

   ```

2. Create virtual enviroment

```bash
python -m venv env
source env/bin/activate
```

```powershell
 ./env/Scripts/activate.ps1

```

3.Install requirements

```bash
  pip install -r requirements.txt
```

4.Run

```bash
   uvicorn src.main:app
```
