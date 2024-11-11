from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'mydb0'
}

# Questions and queries mapping
questions_queries = [
    {
        "question": "Display all records.",
        "query": "SELECT * FROM emp"
    },
    {
        "question": "Display the records of job clerk and manager for deptno 20.",
        "query": """
        SELECT *
        FROM emp
        WHERE job IN ('CLERK', 'MANAGER') AND deptno = 20;
        """
    },
    {
        "question": "Display the records for the employees, which have the last character as R or H in their name.",
        "query": """
        SELECT *
        FROM emp
        WHERE Ename LIKE '%R' OR Ename LIKE '%H';
        """
    },
    {
        "question": "Display the records of the employees earning sal less than 1000 and there is no comm provided.",
        "query": """
        SELECT *
        FROM emp
        WHERE sal < 1000 AND comm IS NULL;
        """
    },
    {
        "question": "Display the ename, sal, comm, sal + comm. For the null value of commission, 10% of sal should be used.",
        "query": """
        SELECT ename AS "Employee Name",
            sal AS Salary,
            comm AS Commission,
            sal + IFNULL(comm, sal * 0.1) AS Total
        FROM emp;
        """
    },
    {
        "question": """
        The raise is to be given under following scenarios –
            a) Employees from deptno 20 from job Clerk should get 30% raise in their salary.
            b) Employees from deptno 20 from job Analyst should get 50% raise in their salary.
            c) Employees from deptno 30 from job Manager should get 60% raise in their salary.
            d) Employees from deptno 30 from job Salesman should get 70% raise in their salary.
            e) Employees from deptno 10 from job Clerk should get 10% raise in their salary.
            f) The remaining employees should get the raise of 500.
        """,
        "query": """
        SELECT ename AS "Employee Name",
            sal AS Salary,
            job,
            deptno AS "Department No",
            CASE
                WHEN deptno = 20 AND job = "CLERK" THEN sal * 0.3
                WHEN deptno = 20 AND job = "ANALYST" THEN sal * 0.5
                WHEN deptno = 30 AND job = "MANAGER" THEN sal * 0.6
                WHEN deptno = 30 AND job = "SALESMAN" THEN sal * 0.7
                WHEN deptno = 10 AND job = "CLERK" THEN sal * 0.1
                ELSE sal + 500
            END AS "Raise in Salary"
        FROM emp;
        """
    },
    {
        "question": "Display name, salary, 30% of salary as tax and salary – tax as take home salary for records of employee table working in deptno 20.",
        "query": """
        SELECT Ename,
            sal AS Salary,
            sal * 0.3 AS "Tax",
            sal - sal * 0.3 AS "Take home salary"
        FROM emp
        WHERE deptno = 20;
        """
    },
    {
        "question": "Display the average, lowest, highest, and difference in lowest and highest salaries for each department number.",
        "query": """
        SELECT deptno AS "Department No",
            AVG(sal) AS Average,
            MIN(sal) AS Lowest,
            MAX(sal) AS Highest,
            MAX(sal) - MIN(sal) AS Difference
        FROM emp
        GROUP BY deptno;
        """
    },
    {
        "question": "Display the lowest salaries job-wise within each department number.",
        "query": """
        SELECT deptno AS "Department No",
            job,
            MIN(sal) AS "Lowest Salary"
        FROM emp
        GROUP BY deptno, job
        ORDER BY deptno, job;
        """
    },
    {
        "question": "Display the records sorted as per the job. Make sure that within each job the records are sorted as per the highest to lowest salaries.",
        "query": """
        SELECT *
        FROM emp
        ORDER BY job, sal DESC;
        """
    },
    {
        "question": "Display Deptno, total of that deptno and Grade. Grade should be A if the total is greater than 10000, else it should be B. Sort the summary output as per the highest to lowest Grade.",
        "query": """
        SELECT deptno AS "Department No",
            SUM(sal) AS Total,
            CASE
                WHEN SUM(sal) > 10000 THEN 'A'
                ELSE 'B'
            END AS Grade
        FROM emp
        GROUP BY deptno
        ORDER BY 2 DESC;
        """
    }
]


# Number of questions per page
QUESTIONS_PER_PAGE = 1

@app.route('/')
def display_questions():
    # Get the current page number from URL query parameters, default is 1
    page = request.args.get('page', 1, type=int)
    
    # Calculate the starting and ending index for the current page
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    # Get questions for the current page
    questions_page = questions_queries[start:end]

    results = []
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        for item in questions_page:
            cursor.execute(item['query'])
            result = cursor.fetchall()
            results.append({"question": item["question"], "query": item["query"], "output": result})

        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        results = []

    # Check if there is a next or previous page
    next_page = page + 1 if end < len(questions_queries) else None
    prev_page = page - 1 if page > 1 else None

    # Render the template with questions and query results
    return render_template('questions.html', results=results, next_page=next_page, prev_page=prev_page)

if __name__ == '__main__':
    app.run(debug=True)
