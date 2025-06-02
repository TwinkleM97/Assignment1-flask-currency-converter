
# Flask Currency Converter

A Flask web application that provides currency conversion functionality with a frontend and RESTful API endpoints.

---

## Technologies Used

- **Python 3.9** (Flask, Requests, Unittest)
- **HTML/CSS/JS** (Frontend)
- **Docker** (Containerization)
- **GitHub Actions** (CI/CD Pipeline)

---

## Folder Structure

```
.
├── app.py                     # Flask application code
├── Dockerfile                 # Docker container definition
├── requirements.txt           # Python dependencies
├── test_app.py                # Unittest-based test cases
├── templates/
│   └── index.html             # Frontend HTML page
└── .github/
    └── workflows/
        └── flask-currency-converter-ci.yml   # CI/CD workflow
```

---

## Dockerfile

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

---

## CI/CD Pipeline Steps (GitHub Actions)

### Workflow Trigger

- Triggered on **Pull Request** to `twinkle-8894858` (main branch).

### Jobs Overview

1️⃣ **build-and-test**
- **Purpose**: Build project and run tests.
- **Steps**:
  - Checkout repository.
  - Setup Python 3.9.
  - Install dependencies.
  - Run unittests via `unittest`.

2️⃣ **docker-build-and-run**
- **Purpose**: Build and run Docker container.
- **Steps**:
  - Build Docker image using `Dockerfile`.
  - Run container in detached mode (`-d`) on port 5000.
  - Wait 10 seconds to ensure app starts.
  - List running containers.
  - Stop and remove the container.

---

## Pipeline Implementation Details

| Stage                  | Details                                                   |
|------------------------|-----------------------------------------------------------|
| Build Project          | Install Python dependencies via `pip`.                     |
| Run Tests              | Execute `test_app.py` with unittests.                      |
| Docker Build           | Build image named `flask-currency-converter` with SHA tag. |
| Docker Run             | Run the Flask app in Docker (`python app.py`).             |
| Container Verification | Display container list, then stop and remove it.          |

---

## Running the App Manually

### Local Python (Without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
```

### Using Docker
```bash
# Build Docker image
docker build -t flask-currency-converter .

# Run container
docker run -d -p 5000:5000 flask-currency-converter

# Access app at http://localhost:5000
```

---

##  Branching Strategy

| Branch                      | Purpose                                             |
|-----------------------------|-----------------------------------------------------|
| `twinkle-8894858` (main)    | Stable main branch.               |
| `feature-assignment1-twinkle` | Feature development branch with all code, tests, CI. |

--
