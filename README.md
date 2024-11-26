# FastAPI Document Encoder and Search
This project provides a FastAPI application for encoding documents and searching through them using sentence embeddings. The application uses the `sentence-transformers` library to generate embeddings and store them for later retrieval.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the FastAPI application:
    ```bash
    uvicorn main:app --reload
    ```

2. The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Encode Documents

- **URL:** `/encode_documents`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "documents": ["Article 1 : Toute personne a droit au respect de sa vie privée...", "Le climat change, il est temps d'agir.", ...]
    }
    ```
- **Response:**
    ```json
    {
        "status": "success",
        "message": "Documents encoded and stored successfully"
    }
    ```

### Search Documents

- **URL:** `/search_documents`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "query": "Droit à la vie privée"
    }
    ```
- **Response:**
    ```json
    {
        "relevant_documents": [
            {
                "id": 1,
                "text": "Article 1 : Toute personne a droit au respect de sa vie privée...",
                "similarity_score": 0.89
            },
            ...
        ]
    }
    ```

## Code Overview

### Main Components

- **FastAPI Application:** Initializes the FastAPI app and defines the endpoints.
- **SentenceTransformer Model:** Loads the `paraphrase-MiniLM-L6-v2` model for encoding sentences.
- **Document and Query Models:** Define the request body structure using Pydantic.
- **Embedding Functions:** Functions to save and load embeddings from a JSON file.
- **Endpoint Handlers:** Functions to handle the `/encode_documents` and `/search_documents` endpoints.

### Error Handling

The application includes error handling for file I/O operations, JSON decoding, and encoding processes. HTTP exceptions are raised with appropriate status codes and messages.

## Watchdog Integration

A watchdog script has been added to automatically detect new `.txt` files in the `documents` directory and send them to the `/encode_documents` endpoint for encoding. This ensures that any new documents added to the directory are processed without manual intervention.

## Composite API Workflow

The watchdog script scans for new `.txt` files with documents. When a new file is detected, it calls the composite API, which then:
1. Calls the embedding service to generate embeddings.
2. Calls the insertion service to store the embeddings in the database.

When a search request is made, the composite API:
1. Calls the embedding service to generate embeddings for the query.
2. Calls the search service to find relevant documents in the database.
3. Uses ChatGPT to generate a response for the client.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
