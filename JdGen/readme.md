
# AI HR - Job Description API

This project is a Flask-based backend service for an AI-powered Human Resources tool. It leverages the Google Gemini API to generate structured job descriptions (JDs) and manages these JDs in a Google Cloud SQL (MySQL) database.

The API provides endpoints to:
- Generate a new JD using AI.
- Create, Read, Update, and Delete (CRUD) job descriptions in the database.
- List all available jobs.

## Prerequisites

- Python 3.8+
- A Google Cloud Platform (GCP) project with:
    - **Google Gemini API** enabled.
    - **Google Cloud SQL (MySQL)** instance created.
- `gcloud` CLI installed and authenticated locally (`gcloud auth application-default login`).
- A Python virtual environment.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd ai_hr_jd_project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root of the project by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file with your specific credentials:
    ```
    # Gemini API
    GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY"

    # Cloud SQL (MySQL)
    DB_USER="your_db_user"
    DB_PASS="your_db_password"
    DB_NAME="your_db_name"
    INSTANCE_CONNECTION_NAME="your_project:your_region:your_instance_name"
    # PRIVATE_IP="true" # Uncomment and set to "true" if connecting via a private IP
    ```

5.  **Run the application:**
    ```bash
    python run.py
    ```
    The server will start, typically on `http://127.0.0.1:8080`.

---

## API Endpoint Documentation

The base URL for all endpoints is `/api/jd`.

### 1. Generate a Job Description

Uses the Gemini API to generate a structured job description based on user inputs.

- **Endpoint:** `POST /api/jd/generate`
- **Description:** Takes basic job details and returns a fully-formed, structured JD in JSON format. This output can then be used to create a new JD entry in the database.
- **Request Body:**
    ```json
    {
      "job_title_input": "Senior Backend Engineer (Python)",
      "key_responsibilities_input": [
        "Develop and maintain scalable backend services",
        "Design and implement RESTful APIs",
        "Collaborate with front-end developers"
      ],
      "required_skills_input": [
        "5+ years of Python experience",
        "Experience with Flask or Django",
        "Knowledge of SQL and ORMs"
      ],
      "company_description_input": "A fast-growing tech startup in the e-commerce space."
    }
    ```
- **Success Response (200 OK):**
    Returns the structured `JobDescriptionContent` object.
    ```json
    {
      "job_title": "Senior Backend Engineer (Python)",
      "company_summary": "Join a fast-growing tech startup...",
      "role_summary": "We are seeking an experienced Senior Backend Engineer...",
      "key_responsibilities": [
        "Develop, test, and deploy robust backend services using Python.",
        "Design, build, and maintain efficient, reusable, and reliable RESTful APIs.",
        "Collaborate with cross-functional teams..."
      ],
      "required_qualifications": [
        "5+ years of professional experience in backend development with Python.",
        "Proven experience with web frameworks such as Flask or Django.",
        "Strong proficiency with SQL databases (e.g., MySQL, PostgreSQL) and ORMs (e.g., SQLAlchemy)."
      ],
      "preferred_qualifications": [
        "Experience with cloud platforms like GCP or AWS.",
        "Familiarity with containerization technologies (Docker, Kubernetes)."
      ],
      "benefits": [
        "Competitive salary and stock options.",
        "Comprehensive health, dental, and vision insurance."
      ]
    }
    ```
- **Error Response (422 Unprocessable Entity):**
    If the request body is missing required fields or has incorrect data types.

### 2. Create a New Job Description

Saves a structured job description to the database.

- **Endpoint:** `POST /api/jd`
- **Description:** Takes a complete JD (typically from the `/generate` endpoint), an expiration time, and saves it to the database. The status defaults to `active`.
- **Request Body:**
    ```json
    {
      "job_title": "Senior Backend Engineer (Python)",
      "jd_content": {
        "job_title": "Senior Backend Engineer (Python)",
        "company_summary": "...",
        "role_summary": "...",
        "key_responsibilities": ["..."],
        "required_qualifications": ["..."],
        "preferred_qualifications": ["..."],
        "benefits": ["..."]
      },
      "expires_at": "2024-12-31T23:59:59Z"
    }
    ```
- **Success Response (201 Created):**
    ```json
    {
      "job_id": 1,
      "message": "JD created successfully"
    }
    ```
- **Error Response (422 Unprocessable Entity):**
    If the request body does not conform to the required schema.

### 3. Get a List of All Job Descriptions

Retrieves a summary list of all JDs in the database.

- **Endpoint:** `GET /api/jd`
- **Description:** Returns a list containing the `id` and `job_title` for every job description stored. Ideal for populating a list view.
- **Request Body:** None
- **Success Response (200 OK):**
    ```json
    [
      {
        "id": 1,
        "job_title": "Senior Backend Engineer (Python)"
      },
      {
        "id": 2,
        "job_title": "Frontend Developer (React)"
      }
    ]
    ```

### 4. Get a Specific Job Description

Retrieves the full details of a single job description by its ID.

- **Endpoint:** `GET /api/jd/{job_id}`
- **Description:** Fetches and returns the complete record for a specific job.
- **Request Body:** None
- **Success Response (200 OK):**
    ```json
    {
      "id": 1,
      "job_title": "Senior Backend Engineer (Python)",
      "jd_content": {
          "job_title": "Senior Backend Engineer (Python)",
          "company_summary": "...",
          "role_summary": "...",
          "key_responsibilities": ["..."],
          "required_qualifications": ["..."],
          "preferred_qualifications": ["..."],
          "benefits": ["..."]
      },
      "created_at": "2023-10-27T10:00:00Z",
      "expires_at": "2024-12-31T23:59:59Z",
      "status": "active"
    }
    ```
- **Error Response (404 Not Found):**
    If a job with the specified `job_id` does not exist.

### 5. Update a Job Description

Modifies an existing job description.

- **Endpoint:** `PUT /api/jd/{job_id}`
- **Description:** Updates one or more fields of a specific JD. All fields in the request body are optional.
- **Request Body:**
    ```json
    {
      "job_title": "Lead Backend Engineer",
      "status": "inactive",
      "jd_content": {
        "job_title": "Lead Backend Engineer",
        "role_summary": "An updated role summary for a lead position...",
        "key_responsibilities": ["..."],
        "required_qualifications": ["..."],
        "preferred_qualifications": ["..."],
        "benefits": ["..."]
      }
    }
    ```
- **Success Response (200 OK):**
    Returns the complete, updated job description object.
    ```json
    {
      "id": 1,
      "job_title": "Lead Backend Engineer",
      "jd_content": { "... updated content ..." },
      "created_at": "2023-10-27T10:00:00Z",
      "expires_at": "2024-12-31T23:59:59Z",
      "status": "inactive"
    }
    ```
- **Error Responses:**
    - `404 Not Found`: If the `job_id` does not exist.
    - `422 Unprocessable Entity`: If the request body contains invalid data (e.g., `status` is not 'active' or 'inactive').

### 6. Delete a Job Description

Permanently removes a job description from the database.

- **Endpoint:** `DELETE /api/jd/{job_id}`
- **Description:** Deletes the JD record corresponding to the given `job_id`.
- **Request Body:** None
- **Success Response (200 OK):**
    ```json
    {
      "message": "Job Description deleted successfully"
    }
    ```
- **Error Response (404 Not Found):**
    If a job with the specified `job_id` does not exist.

---

## Database Schema

The application uses a single table named `job_descriptions` in a MySQL database.

### Table: `job_descriptions`

This table stores all the job descriptions managed by the system.

| Column Name       | Data Type                  | Constraints & Description                                       |
|-------------------|----------------------------|-----------------------------------------------------------------|
| `id`              | `INTEGER`                  | **Primary Key**, Auto-incrementing, Indexed.                    |
| `job_title`       | `VARCHAR(255)`             | **Not Null**, Indexed. The main title of the job for easy querying. |
| `jd_content_json` | `TEXT` or `LONGTEXT`       | **Not Null**. Stores the full, structured JD as a JSON string.    |
| `created_at`      | `DATETIME`                 | **Not Null**. Defaults to the current UTC timestamp on creation.  |
| `expires_at`      | `DATETIME`                 | Nullable. The timestamp when the job posting should expire.     |
| `status`          | `ENUM('active','inactive')`| **Not Null**. Defaults to `'active'`. The current status of the job. |

<br>

### `CREATE TABLE` Statement

Here is the equivalent SQL `CREATE TABLE` statement for the schema defined by the SQLAlchemy model.

```sql
CREATE TABLE job_descriptions (
    id INT AUTO_INCREMENT NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    jd_content_json TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME,
    status ENUM('active', 'inactive') NOT NULL,
    PRIMARY KEY (id),
    INDEX ix_job_descriptions_job_title (job_title),
    INDEX ix_job_descriptions_id (id)
);
```