import os
import re
import uuid
import json
import matplotlib.pyplot as plt
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from config import API_KEY, PLOT_DIR
from database import fetch_schema, run_query
import logging

logger = logging.getLogger(__name__)

plt.switch_backend("Agg")


# --- LLM Setup ---
def get_llm():
    if not API_KEY or API_KEY.startswith("sk-or-v1-3f5485"):
        logger.warning("[Warning] Using a placeholder/invalid API Key.")
        return None
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
        model="deepseek/deepseek-chat",  # "anthropic/claude-3-haiku",
        temperature=0.1,
    )


# --- Prompts ---
ROUTER_PROMPT = PromptTemplate.from_template(
    """
    You are a classification assistant. Your job is to determine if a user's question
    is a 'greeting' (like hi, hello, how are you, who are you), a 'goodbye' (like bye, see you),
    or a 'database_query' (asking for data, counts, trends, plots, customers, visits).
    User Question: {question}
    Output ONLY 'greeting', 'goodbye', or 'database_query'.
    """
)

GREETING_PROMPT = PromptTemplate.from_template(
    """
    You are 'FaceTrack AI', a helpful assistant for the Face Recognition Customer Management System.
    The user said: {question}.
    Respond with a friendly greeting (1-2 sentences). Briefly mention your capabilities: I can answer questions about customer data, generate plots, and help you manage your face recognition system.
    """
)

GOODBYE_PROMPT = PromptTemplate.from_template(
    """
    You are 'FaceTrack AI'. The user said: {question}. Respond with a brief, friendly goodbye.
    """
)

SQL_PROMPT = PromptTemplate.from_template(
    """
    You are an expert SQL assistant. Given the schema: {schema}
    And the user question: {question}
    Write a VALID MySQL query. Only output the SQL query. Do not add ```sql or explanations.
    If the question is about 'today', use CURDATE().
    If asking for 'top' customers, use ORDER BY visit_count DESC.
    """
)

SUMMARY_PROMPT = PromptTemplate.from_template(
    """
    Given the SQL result: {result}. Write a short (1-3 sentences), human-friendly summary.
    If the result is empty, say 'No data found for that query.'
    """
)

VISUALIZATION_PROMPT = PromptTemplate.from_template(
    """
    You are a data visualization advisor. Given a user question '{question}'
    and SQL results (list of tuples): {result}.
    The available plot types are 'bar', 'line', 'pie'.
    Decide the BEST plot type. If unsure, 'bar' is a safe default.
    Identify the column index for the X-axis (labels) and the Y-axis (values).
    For pie charts, use Y-axis for values and X-axis for labels.
    If only one column exists (e.g., COUNT(*)), use it for Y and generate simple labels.
    Suggest a suitable title.
    Output ONLY a JSON object: {{"plot_type": "bar", "x_index": 0, "y_index": 1, "title": "Your Title"}}
    If no visualization seems appropriate from the data, or if the data is empty, output ONLY {{"plot_type": "none"}}.
    """
)

VISUALIZATION_KEYWORDS = [
    "plot",
    "graph",
    "visualize",
    "chart",
    "show me",
    "draw",
    "picture",
    "visual",
]


# --- SQL & Summary ---
def clean_sql_output(response):
    cleaned = re.sub(r"^```sql|```$", "", response.strip(), flags=re.IGNORECASE).strip()
    if cleaned.lower().startswith("sql"):
        cleaned = cleaned[3:].strip()
    return cleaned


def generate_sql(question, schema):
    llm = get_llm()
    if not llm:
        return "SELECT 'API Key Missing';"
    prompt = SQL_PROMPT.format(question=question, schema=schema)
    response = llm.invoke(prompt).content
    return clean_sql_output(response)


def summarize_result(results):
    llm = get_llm()
    if not llm:
        return "Summary unavailable (API Key Missing)."
    if not results:
        return "No data found for that query."
    prompt = SUMMARY_PROMPT.format(result=str(results))
    return llm.invoke(prompt).content


# --- Plotting ---
def get_visualization_advice(question, results):
    llm = get_llm()
    if not llm or not results:
        return None
    prompt = VISUALIZATION_PROMPT.format(question=question, result=str(results))
    response = llm.invoke(prompt).content
    logger.debug(f"LLM Viz Advice Raw: {response}")
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            logger.warning("Could not extract JSON from LLM viz advice.")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding LLM viz advice: {e} - Response: {response}")
        return None


def generate_safe_plot(results, plot_info):
    if not results or not plot_info:
        return None
    try:
        plot_type = plot_info.get("plot_type", "bar")
        x_index = int(plot_info.get("x_index", 0))
        y_index = int(plot_info.get("y_index", 1))
        title = plot_info.get("title", "Generated Plot")

        if (
            not results
            or not results[0]
            or x_index >= len(results[0])
            or y_index >= len(results[0])
        ):
            logger.error(f"Invalid column indices {x_index},{y_index} for results.")
            return None

        labels = [str(row[x_index]) for row in results]
        values = [
            float(row[y_index]) if row[y_index] is not None else 0.0 for row in results
        ]

        plt.figure(figsize=(8, 5))

        if plot_type == "bar":
            plt.bar(labels, values, color="#4f46e5")
            plt.xticks(rotation=45, ha="right")
        elif plot_type == "line":
            plt.plot(labels, values, marker="o", color="#10b981")
            plt.xticks(rotation=45, ha="right")
        elif plot_type == "pie":
            plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
            plt.axis("equal")
        else:
            plt.bar(labels, values, color="#4f46e5")
            plt.xticks(rotation=45, ha="right")

        plt.title(title, fontsize=14)
        plt.tight_layout()

        filename = f"{uuid.uuid4().hex}.png"
        filepath = os.path.join(PLOT_DIR, filename)
        plt.savefig(filepath)
        plt.close()
        logger.info(f"Plot saved as {filepath}")
        return filename
    except Exception as e:
        logger.error(f"Error generating safe plot: {e}")
        return None


# --- Main Handler ---
def handle_question(question):
    llm = get_llm()
    if not llm:
        return "Chatbot is offline (API Key Missing).", None

    try:
        router_prompt_text = ROUTER_PROMPT.format(question=question)
        route = llm.invoke(router_prompt_text).content.strip().lower()
        logger.info(f"Chat Route: {route}")

        if "greeting" in route:
            prompt = GREETING_PROMPT.format(question=question)
            return llm.invoke(prompt).content, None
        elif "goodbye" in route:
            prompt = GOODBYE_PROMPT.format(question=question)
            return llm.invoke(prompt).content, None
        elif "database_query" in route:
            schema = fetch_schema()
            want_visual = any(
                keyword in question.lower() for keyword in VISUALIZATION_KEYWORDS
            )
            plot_filename = None
            sql_query = generate_sql(question, schema)
            logger.info(f"[Generated SQL] {sql_query}")

            results = run_query(sql_query)
            logger.info(f"[SQL Results] {results}")

            summary = summarize_result(results)

            if want_visual and results:
                plot_info = get_visualization_advice(question, results)
                if plot_info and plot_info.get("plot_type") != "none":
                    plot_filename = generate_safe_plot(results, plot_info)

            return summary, plot_filename
        else:
            return (
                "I can help with greetings or questions about customer data. How can I assist you?",
                None,
            )
    except Exception as e:
        logger.error(f"Error handling question '{question}': {e}")
        return "Sorry, I encountered an error. Please try again or rephrase.", None
