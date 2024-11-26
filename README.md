# Document Embedding and Search API

This repository provides a FastAPI-based system for encoding documents, storing them as embeddings, and performing searches to retrieve relevant results. It integrates multiple services to streamline document management and query handling, including embedding generation, database storage, and query augmentation.

## Features

- **Document Embedding:** Uses `sentence-transformers` to generate embeddings from textual data.
- **Database Storage:** Stores embeddings and corresponding documents in a MariaDB database.
- **Search Functionality:** Allows users to query stored documents by relevance using cosine similarity.
- **Web Interface:** A user-friendly web interface for submitting queries and viewing results.
- **Watchdog Script:** Automatically detects new `.txt` files in a specified directory and processes them.

---

## Installation

### Prerequisites

- Python 3.9 or above
- MariaDB installed and running
- Required Python libraries (see `requirements.txt`)

### Steps

1. **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Set Up a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure MariaDB:**
    - Create a database named `workflow_db`.
    - Set up a user with appropriate credentials.
    - Update `config.py` with the database connection string.

    ```python
    DATABASE_URL = "mariadb+pymysql://user:password@localhost/workflow_db"
    ```

5. **Ensure Directory Structure:**
    - Create the `documents` folder to store `.txt` files for automatic embedding.
    - Include `templates/` and `static/` directories for the web interface.

---

## Usage

### Starting the Services

1. **Run All Services:**
    Use the launcher script to start the system:
    ```bash
    python launch_services.py
    ```

2. **Access the Web Interface:**
    Open your browser and go to [http://127.0.0.1:8003](http://127.0.0.1:8003).

### Endpoints Overview

#### 1. Embedding Service
- **URL:** `http://127.0.0.1:8001/embed`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "documents": ["Your text here"]
    }
    ```
- **Response:**
    ```json
    {
        "embeddings": [[...]]
    }
    ```

#### 2. Database Service
- **Insert Embedding:**
  - **URL:** `http://127.0.0.1:8002/insert_embedding/`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
        "document_text": "Your text here",
        "embedding": [...]
    }
    ```
- **Search Embeddings:**
  - **URL:** `http://127.0.0.1:8002/search_embeddings/`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    [0.1, 0.2, 0.3, ...]  # Example embedding vector
    ```

#### 3. Composite API
- **Process Document:**
  - **URL:** `http://127.0.0.1:8000/process_document`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
        "documents": ["Your text here"]
    }
    ```
- **Search Documents:**
  - **URL:** `http://127.0.0.1:8000/search`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
        "query": "Your search term"
    }
    ```

---

## Architecture Overview

1. **Watchdog Script:**
    - Monitors the `documents` directory for new `.txt` files.
    - Sends the detected files to the composite API for processing.

2. **Composite API Workflow:**
    - Calls the embedding service to generate embeddings.
    - Stores embeddings in the database using the database service.
    - Handles query embedding and retrieves relevant documents from the database.

3. **Web Interface:**
    - Provides a simple form for users to submit queries.
    - Displays top results based on similarity.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
