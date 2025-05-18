import os
import re
import pymysql
import sqlparse
import pandas as pd
import matplotlib.pyplot as plt
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from config import DB_CONFIG, API_KEY


# Prompt templates
SQL_PROMPT = PromptTemplate.from_template(
    """
    You are an expert SQL assistant. Given the schema:
    {schema}

    And the user question:
    {question}

    Write a VALID MySQL query to answer the question.
    Only output the SQL query, no explanation.
    """
)

SUMMARY_PROMPT = PromptTemplate.from_template(
    """
    Given the SQL result:
    {result}

    Write a short, human-friendly summary of the insight or pattern it shows.
    """
)

VISUALIZATION_PROMPT = PromptTemplate.from_template(
    """
    You are a Python expert who writes matplotlib code for data visualization.
    Given the SQL query result data as a Python list of tuples:
    {result}

    Write a complete python code snippet to plot an appropriate chart (bar, line, pie, etc.) that visually represents the data.
    Make sure to include import statements and plt.show().
    """
)

VISUALIZATION_KEYWORDS = [
    "plot",
    "graph",
    "visualize",
    "chart",
    "bar chart",
    "line chart",
    "drawing",
    "painting",
    "diagram",
    "sketch",
    "illustration",
    "figure",
    "display",
    "show me",
    "draw",
    "picture",
    "plotting",
    "visual",
    "bar graph",
    "histogram",
    "pie chart",
]

def fetch_all_customers(conn):
    cursor = conn.cursor()
    query = (
        """SELECT unique_id, name, email, last_visited, visit_count FROM customers"""
    )
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    return df

def generate_visit_history_report(conn, output_csv="visit_history_report.csv"):
    df = fetch_all_customers(conn)
    df.to_csv(output_csv, index=False)
    print(f"Customer visit history exported to {output_csv}")
    return df


def plot_visit_analytics(conn):
    df = fetch_all_customers(conn)
    if df.empty:
        print("No customer data available for analytics.")
        return
    # Plot: Most frequent visitors
    top_visitors = df.sort_values("visit_count", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.bar(top_visitors["unique_id"], top_visitors["visit_count"])
    plt.xlabel("Customer ID")
    plt.ylabel("Visit Count")
    plt.title("Top 10 Most Frequent Visitors")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    # Plot: Visits over time (if last_visited is not null)
    if df["last_visited"].notnull().any():
        df["last_visited"] = pd.to_datetime(df["last_visited"], errors="coerce")
        df = df.dropna(subset=["last_visited"])
        df["date"] = df["last_visited"].dt.date
        visits_per_day = df.groupby("date").size()
        plt.figure(figsize=(10, 6))
        visits_per_day.plot(kind="bar")
        plt.xlabel("Date")
        plt.ylabel("Number of Visits")
        plt.title("Visits Per Day")
        plt.tight_layout()
        plt.show()
    else:
        print("No last_visited data to plot visits over time.")


def export_customers_to_excel(conn, output_excel="customers_export.xlsx"):
    df = fetch_all_customers(conn)
    df.to_excel(output_excel, index=False)
    print(f"Customer data exported to {output_excel}")

def fetch_schema(cursor):
    """Fetch the schema of all tables in the database."""
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = ""
    for (table,) in tables:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        cols = cursor.fetchall()
        schema += f"\nTable `{table}`:\n"
        for col in cols:
            schema += f"  - {col[0]} ({col[1]})\n"
    return schema


def is_valid_sql(query):
    """Check if the SQL query is valid using sqlparse."""
    try:
        parsed = sqlparse.parse(query)
        return len(parsed) > 0
    except Exception:
        return False


def run_query(query):
    """Run a SQL query and return the results."""
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    connection.close()
    return results


def clean_sql_output(response):
    """Clean LLM output to extract the SQL query only."""
    cleaned = re.sub(r"^```sql|```$", "", response.strip(), flags=re.IGNORECASE).strip()
    if cleaned.lower().startswith("sql"):
        cleaned = cleaned[3:].strip()
    return cleaned


def generate_sql(question, schema, llm=None):
    """Generate a SQL query from a user question and schema using LLM."""
    if llm is None:
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=API_KEY,
            model="deepseek/deepseek-chat",
        )
    prompt = SQL_PROMPT.format(question=question, schema=schema)
    response = llm.predict(prompt)
    sql_query = clean_sql_output(response)
    return sql_query


def summarize_result(results, llm=None):
    """Summarize SQL results using LLM."""
    if llm is None:
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=API_KEY,
            model="deepseek/deepseek-chat",
        )
    result_text = str(results)
    prompt = SUMMARY_PROMPT.format(result=result_text)
    try:
        response = llm.predict(prompt)
        return response
    except Exception as e:
        print(f"[Summary Generation Error]: {e}")
        return "Summary generation failed."


def extract_code_from_response(response):
    """Extract python code from LLM response."""
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    else:
        lines = response.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith(("import", "def", "plt", "#")):
                return "\n".join(lines[i:]).strip()
        return response.strip()


def generate_visualization_code(results, llm=None):
    """Generate matplotlib code for visualizing SQL results using LLM."""
    if llm is None:
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=API_KEY,
            model="deepseek/deepseek-chat",
        )
    result_text = str(results)
    prompt = VISUALIZATION_PROMPT.format(result=result_text)
    response = llm.predict(prompt)
    code = extract_code_from_response(response)
    return code


def execute_visualization_code(code):
    """Execute generated matplotlib code and save the plot as output_plot.png."""
    filename = "temp_visualization.py"
    with open(filename, "w") as f:
        f.write(code)
    # Replace plt.show() with plt.savefig
    modified_code = code.replace(
        "plt.show()",
        'plt.savefig("output_plot.png")\nprint("Plot saved as output_plot.png")',
    )
    with open(filename, "w") as f:
        f.write(modified_code)
    os.system(f"python {filename}")
    os.remove(filename)


def handle_question(question):
    """Main entry point: handle a user question, generate SQL, run it, summarize, and visualize if needed."""
    import pymysql

    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        schema = fetch_schema(cursor)
    want_visual = any(keyword in question.lower() for keyword in VISUALIZATION_KEYWORDS)
    for _ in range(2):
        sql_query = generate_sql(question, schema)
        print(f"[Generated SQL] {sql_query}")
        if not is_valid_sql(sql_query):
            print("Invalid SQL syntax. Retrying...")
            continue
        try:
            results = run_query(sql_query)
            print(f"[SQL Results] {results}")
            if want_visual and results:
                print("Generating visualization...")
                vis_code = generate_visualization_code(results)
                print(f"[Visualization Code]\n{vis_code}\n")
                execute_visualization_code(vis_code)
            print("Generating summary...")
            summary = summarize_result(results)
            return summary
        except Exception as e:
            print(f"Error running SQL: {e}")
            continue
    return "Sorry, I couldn't process your request."
