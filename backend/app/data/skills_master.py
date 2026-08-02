"""Master skill catalog.

This is the single source of truth for skill names, categories and aliases.
Aliases allow normalisation of variants such as "Python3", "PYTHON" -> "Python".
"""

from __future__ import annotations

# name -> (category, weight, [aliases...])
SKILL_CATALOG: dict[str, tuple[str, float, list[str]]] = {
    # --- Programming languages ---
    "Python": ("programming_language", 1.0, ["python3", "py", "python 3", "python 2", "py3"]),
    "Java": ("programming_language", 1.0, ["java 8", "java 11", "core java", "java se", "java ee"]),
    "JavaScript": ("programming_language", 1.0, ["js", "es6", "ecmascript"]),
    "TypeScript": ("programming_language", 1.0, ["ts"]),
    "Go": ("programming_language", 1.0, ["golang", "go lang"]),
    "C++": ("programming_language", 1.0, ["cpp", "c plus plus", "c++11", "c++17"]),
    "C": ("programming_language", 0.9, ["ansi c"]),
    "C#": ("programming_language", 1.0, ["csharp", "c sharp", ".net c#"]),
    "Rust": ("programming_language", 1.0, []),
    "Ruby": ("programming_language", 0.9, ["rails ruby"]),
    "PHP": ("programming_language", 0.9, []),
    "Swift": ("programming_language", 0.9, []),
    "Kotlin": ("programming_language", 0.9, []),
    "Scala": ("programming_language", 0.8, []),
    "R": ("programming_language", 0.9, ["r language"]),
    "MATLAB": ("programming_language", 0.7, []),
    "SQL": ("programming_language", 1.0, ["structured query language", "tsql", "pl/sql"]),
    "Bash": ("programming_language", 0.8, ["shell", "shell scripting", "bash scripting"]),
    "PowerShell": ("programming_language", 0.6, []),
    "Groovy": ("programming_language", 0.5, []),
    "Perl": ("programming_language", 0.4, []),
    "Julia": ("programming_language", 0.5, []),
    "Objective-C": ("programming_language", 0.5, []),
    "Visual Basic": ("programming_language", 0.3, ["vb.net", "vba"]),
    "Elixir": ("programming_language", 0.5, []),
    "Haskell": ("programming_language", 0.4, []),
    "COBOL": ("programming_language", 0.3, []),
    # --- Web frameworks ---
    "React": ("web_framework", 1.0, ["react.js", "reactjs", "react js"]),
    "React Native": ("web_framework", 1.0, []),
    "Next.js": ("web_framework", 1.0, ["nextjs", "next js"]),
    "Vue.js": ("web_framework", 1.0, ["vue", "vuejs", "vue 3", "vue 2"]),
    "Angular": ("web_framework", 1.0, ["angularjs", "angular 2", "angular 4", "angular 8", "ng"]),
    "Svelte": ("web_framework", 0.8, ["svelte.js", "sveltekit"]),
    "Django": ("web_framework", 1.0, ["django rest", "django framework"]),
    "Flask": ("web_framework", 0.9, []),
    "FastAPI": ("web_framework", 1.0, []),
    "Spring Boot": ("web_framework", 1.0, ["spring", "spring framework", "spring mvc"]),
    "Ruby on Rails": ("web_framework", 0.9, ["rails"]),
    "Laravel": ("web_framework", 0.8, []),
    "ASP.NET": ("web_framework", 0.9, ["asp.net core", ".net core", ".net"]),
    "Express.js": ("web_framework", 0.9, ["express", "expressjs"]),
    "Node.js": ("web_framework", 1.0, ["node", "nodejs"]),
    "GraphQL": ("web_framework", 0.9, ["apollo"]),
    "JQuery": ("web_framework", 0.6, []),
    "Redux": ("web_framework", 0.8, ["redux toolkit"]),
    "Tailwind CSS": ("web_framework", 0.8, ["tailwind", "tailwindcss"]),
    "Bootstrap": ("web_framework", 0.6, []),
    "Material-UI": ("web_framework", 0.6, ["mui"]),
    "Shadcn": ("web_framework", 0.5, ["shadcn/ui"]),
    # --- Data & ML ---
    "Machine Learning": ("data_science", 1.0, ["ml", "ml models"]),
    "Deep Learning": ("data_science", 1.0, ["deep neural networks"]),
    "Data Science": ("data_science", 1.0, []),
    "Data Engineering": ("data_science", 0.9, []),
    "Data Analysis": ("data_science", 0.9, ["data analytics"]),
    "Data Visualization": ("data_science", 0.7, ["dataviz", "data visualisation"]),
    "Pandas": ("data_science", 1.0, []),
    "NumPy": ("data_science", 1.0, []),
    "SciPy": ("data_science", 0.8, []),
    "scikit-learn": ("data_science", 1.0, ["sklearn"]),
    "TensorFlow": ("data_science", 1.0, ["tf", "keras", "tensor flow"]),
    "PyTorch": ("data_science", 1.0, []),
    "XGBoost": ("data_science", 1.0, ["xg boost"]),
    "LightGBM": ("data_science", 1.0, []),
    "CatBoost": ("data_science", 0.9, []),
    "NLP": ("data_science", 1.0, ["natural language processing", "nl processing"]),
    "Computer Vision": ("data_science", 0.9, ["cv", "image processing"]),
    "LLM": ("data_science", 1.0, ["large language model", "large language models", "llms"]),
    "RAG": ("data_science", 0.9, ["retrieval augmented generation"]),
    "LangChain": ("data_science", 1.0, []),
    "OpenAI API": ("data_science", 0.8, ["openai", "chatgpt api", "gpt"]),
    "SHAP": ("data_science", 0.7, []),
    "MLflow": ("mlops", 0.9, []),
    "Statistical Analysis": ("data_science", 0.8, ["statistics", "stats"]),
    "A/B Testing": ("data_science", 0.7, []),
    "Feature Engineering": ("data_science", 0.8, []),
    "Model Deployment": ("mlops", 0.8, []),
    "Experimentation": ("data_science", 0.6, []),
    # --- Cloud & DevOps ---
    "AWS": ("cloud", 1.0, ["amazon web services", "aws services"]),
    "Azure": ("cloud", 1.0, ["microsoft azure"]),
    "Google Cloud": ("cloud", 1.0, ["gcp", "google cloud platform"]),
    "Docker": ("devops", 1.0, ["containerization"]),
    "Kubernetes": ("devops", 1.0, ["k8s", "kubernetes orchestration"]),
    "Terraform": ("devops", 0.9, ["iac", "infrastructure as code"]),
    "CI/CD": ("devops", 1.0, ["continuous integration", "continuous delivery", "cd pipeline"]),
    "Jenkins": ("devops", 0.8, []),
    "GitHub Actions": ("devops", 0.9, ["gh actions"]),
    "GitLab CI": ("devops", 0.7, ["gitlab"]),
    "Prometheus": ("monitoring", 0.9, []),
    "Grafana": ("monitoring", 0.9, []),
    "Datadog": ("monitoring", 0.8, []),
    "ELK Stack": ("monitoring", 0.8, ["elasticsearch", "logstash", "kibana"]),
    "Linux": ("devops", 1.0, ["unix", "ubuntu", "debian"]),
    "Nginx": ("devops", 0.8, []),
    "Serverless": ("cloud", 0.8, ["lambda", "cloud functions"]),
    "Helm": ("devops", 0.7, []),
    "Ansible": ("devops", 0.7, []),
    "Vault": ("security", 0.6, []),
    "S3": ("cloud", 0.9, ["amazon s3"]),
    # --- Databases ---
    "PostgreSQL": ("database", 1.0, ["postgres", "psql"]),
    "MySQL": ("database", 1.0, []),
    "MongoDB": ("database", 1.0, ["mongo", "mongodb atlas"]),
    "Redis": ("database", 1.0, []),
    "Elasticsearch": ("database", 0.8, ["elastic", "es"]),
    "DynamoDB": ("database", 0.9, ["dynamo"]),
    "Cassandra": ("database", 0.7, []),
    "SQLite": ("database", 0.6, []),
    "Snowflake": ("database", 0.9, []),
    "BigQuery": ("database", 0.9, []),
    "Oracle": ("database", 0.7, ["oracle db", "oracle database"]),
    "SQL Server": ("database", 0.8, ["mssql"]),
    "Firebase": ("database", 0.7, ["firestore", "firebase firestore"]),
    "Neo4j": ("database", 0.6, []),
    "ClickHouse": ("database", 0.6, []),
    "Kafka": ("data_engineering", 1.0, ["apache kafka"]),
    "Airflow": ("data_engineering", 0.9, ["apache airflow"]),
    "Spark": ("data_engineering", 1.0, ["apache spark", "pyspark", "spark sql"]),
    "Hadoop": ("data_engineering", 0.7, []),
    "dbt": ("data_engineering", 0.8, ["data build tool"]),
    "ETL": ("data_engineering", 0.8, ["elt", "data pipelines"]),
    # --- Software engineering ---
    "Git": ("software_engineering", 1.0, ["git version control", "github", "gitlab"]),
    "REST APIs": ("software_engineering", 1.0, ["rest", "restful api", "rest api", "api design"]),
    "Microservices": ("software_engineering", 0.9, []),
    "System Design": ("software_engineering", 0.9, ["distributed systems", "architecture design"]),
    "Testing": ("software_engineering", 0.8, ["unit testing", "test driven development", "tdd"]),
    "Pytest": ("software_engineering", 0.7, []),
    "Jest": ("software_engineering", 0.7, []),
    "Agile": ("software_engineering", 0.6, ["scrum", "kanban"]),
    "SOLID": ("software_engineering", 0.6, ["solid principles"]),
    "Design Patterns": ("software_engineering", 0.7, []),
    "SQLAlchemy": ("software_engineering", 0.9, []),
    "Celery": ("software_engineering", 0.8, []),
    "Message Queues": ("software_engineering", 0.7, ["rabbitmq", "message brokers"]),
    "Web Scraping": ("software_engineering", 0.6, ["scrapy", "beautifulsoup"]),
    "Gunicorn": ("software_engineering", 0.6, []),
    "WebSockets": ("software_engineering", 0.6, []),
    "OAuth2": ("security", 0.8, ["oauth", "oauth 2.0"]),
    "JWT": ("security", 0.9, ["json web token", "json web tokens"]),
    # --- Generative AI ---
    "Generative AI": ("generative_ai", 0.9, ["genai", "gen ai"]),
    "Prompt Engineering": ("generative_ai", 0.8, []),
    "Fine-tuning": ("generative_ai", 0.9, ["model fine tuning", "fine tuning"]),
    "Transformers": ("generative_ai", 0.8, ["huggingface", "hugging face"]),
    "Vector Databases": ("generative_ai", 0.8, ["pgvector", "pinecone", "weaviate", "qdrant", "chroma"]),
    "AI Agents": ("generative_ai", 0.9, ["agents", "agentic ai"]),
    # --- Business / soft skills ---
    "Communication": ("soft_skill", 0.5, ["communication skills"]),
    "Leadership": ("soft_skill", 0.5, []),
    "Project Management": ("soft_skill", 0.6, ["project planning", "pmp"]),
    "Team Collaboration": ("soft_skill", 0.5, ["collaboration", "teamwork"]),
    "Problem Solving": ("soft_skill", 0.6, ["analytical skills"]),
    "Product Management": ("soft_skill", 0.7, ["product"]),
    "Stakeholder Management": ("soft_skill", 0.5, ["stakeholder communication"]),
    "Mentoring": ("soft_skill", 0.5, ["mentorship", "coaching"]),
    "Public Speaking": ("soft_skill", 0.4, ["presentations"]),
    "Strategic Planning": ("soft_skill", 0.5, []),
    # --- Product / design ---
    "Figma": ("design", 0.6, []),
    "UI/UX Design": ("design", 0.6, ["ui design", "ux design", "user experience"]),
    "Product Analytics": ("product", 0.6, ["amplitude", "mixpanel"]),
    "SQL Analytics": ("product", 0.7, []),
    # --- Office ---
    "Excel": ("office", 0.6, ["microsoft excel", "advanced excel", "excel vba"]),
    "Power BI": ("office", 0.7, ["powerbi", "power bi dashboards"]),
    "Tableau": ("office", 0.7, []),
    "Google Sheets": ("office", 0.5, []),
    "Jira": ("office", 0.5, ["jira atlassian"]),
    "Confluence": ("office", 0.4, []),
    "Notion": ("office", 0.4, []),
    "Slack": ("office", 0.3, []),
}


def build_skill_index() -> dict[str, dict]:
    """Build a lookup index mapping every alias to its canonical skill."""
    index: dict[str, dict] = {}
    for name, (category, weight, aliases) in SKILL_CATALOG.items():
        entry = {"name": name, "category": category, "weight": weight}
        normalized = normalize_skill_token(name)
        index[normalized] = entry
        for alias in aliases:
            index[normalize_skill_token(alias)] = entry
    return index


def normalize_skill_token(token: str) -> str:
    """Normalise a skill token for fuzzy lookup (lowercase, trimmed, deduped)."""
    return " ".join(token.strip().lower().split())


def get_canonical_skill(token: str) -> dict | None:
    """Return the canonical skill entry for a token, or None."""
    return SKILL_INDEX.get(normalize_skill_token(token))


def all_skills() -> list[dict]:
    """Return the full catalog as a list of skill dicts."""
    return [
        {"name": name, "category": category, "weight": weight} for name, (category, weight, _) in SKILL_CATALOG.items()
    ]


SKILL_INDEX = build_skill_index()
