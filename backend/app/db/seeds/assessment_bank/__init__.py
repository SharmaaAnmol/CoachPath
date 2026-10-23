"""Assessment question bank package."""
from .python_questions import PYTHON_QUESTIONS
from .javascript_typescript_questions import JAVASCRIPT_TYPESCRIPT_QUESTIONS
from .java_questions import JAVA_QUESTIONS
from .c_cpp_questions import C_CPP_QUESTIONS
from .sql_databases_questions import SQL_DATABASES_QUESTIONS
from .dsa_questions import DSA_QUESTIONS
from .web_development_questions import WEB_DEVELOPMENT_QUESTIONS
from .machine_learning_questions import MACHINE_LEARNING_QUESTIONS
from .ai_llm_questions import AI_LLM_QUESTIONS

__all__ = [
    "PYTHON_QUESTIONS",
    "JAVASCRIPT_TYPESCRIPT_QUESTIONS",
    "JAVA_QUESTIONS",
    "C_CPP_QUESTIONS",
    "SQL_DATABASES_QUESTIONS",
    "DSA_QUESTIONS",
    "WEB_DEVELOPMENT_QUESTIONS",
    "MACHINE_LEARNING_QUESTIONS",
    "AI_LLM_QUESTIONS",
]
