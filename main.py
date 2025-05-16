import sqlite3
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="Database Chat API")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
       
        "http://localhost:8001",  # For testing backend directly
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(api_key="")

# Pydantic model for request body
class QuestionRequest(BaseModel):
    question: str

# Function to create SQLite database and table
def setup_database():
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mydb (
            name TEXT PRIMARY KEY,
            age INTEGER,
            location TEXT,
            gender TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM mydb")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('Nagendhar', 30, 'Hyderabad', 'Male'),
            ('Priya', 25, 'Bangalore', 'Female'),
            ('Arun', 35, 'Chennai', 'Male'),
            ('Sneha', 28, 'Mumbai', 'Female')
        ]
        cursor.executemany('INSERT INTO mydb (name, age, location, gender) VALUES (?, ?, ?, ?)', sample_data)
    
    conn.commit()
    conn.close()

# Function to clean the generated SQL query
def clean_sql_query(query):
    cleaned = re.sub(r'```sql\s*|\s*```', '', query)
    return cleaned.strip()

# Function to generate SQL query using Groq
def generate_sql_query(question: str) -> str:
    prompt = f"""
    You are a SQL query generator for a SQLite database with a table 'mydb' having columns: 
    - name (TEXT, PRIMARY KEY)
    - age (INTEGER)
    - location (TEXT)
    - gender (TEXT)
    
    Based on the user's question: "{question}", generate a valid SQLite SELECT query to retrieve the requested information. 
    - Return ONLY the SQL query as plain text.
    - Do NOT wrap the query in markdown code blocks.
    - Do NOT include explanations or comments.
    - Ensure the query is safe and uses proper SQLite syntax.
    - If the question implies a specific column, select only that column.
    - If the question is vague, select all relevant columns.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=False,
    )
    
    return clean_sql_query(chat_completion.choices[0].message.content)

# Function to execute SQL query and get raw results
def execute_query(query: str):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return None
        
        formatted_results = []
        for row in results:
            formatted_results.append(dict(zip(columns, row)))
        return formatted_results
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error executing query: {e}")

# Function to generate a descriptive answer based on the query results
def generate_descriptive_answer(question: str, results, query: str):
    if results is None or len(results) == 0:
        return "I couldn't find any matching information in the database."
    
    prompt = f"""
    You are a helpful assistant for a database application. Based on the user's question and the database query results, 
    provide a natural language answer that directly addresses the question in a descriptive way.
    
    User's question: "{question}"
    
    Database query: {query}
    
    Query results: {results}
    
    Respond with ONLY the answer in natural language. Make it conversational but direct. 
    Don't include explanations about the query or how you got the answer.
    Ensure the answer is descriptive and provides context about what was asked.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=False,
    )
    
    return chat_completion.choices[0].message.content.strip()

# Setup database on startup
@app.on_event("startup")
async def startup_event():
    setup_database()

# Chat API endpoint
@app.post("/chat")
async def chat(request: QuestionRequest):
    try:
        # Generate and execute SQL query
        sql_query = generate_sql_query(request.question)
        raw_results = execute_query(sql_query)
        
        # Generate a descriptive answer using the LLM
        descriptive_answer = generate_descriptive_answer(request.question, raw_results, sql_query)
        
        return {"question": request.question, "answer": descriptive_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "Database Chat API is running"}
