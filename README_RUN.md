1. Open the project
Open PlantCare_Potato_Project in VS Code.

2. Activate the virtual environment
Open the terminal in the project folder:
".venv\Scripts\activate"  

3. Install dependencies (first time only)
"pip install -r requirements.txt"
if you have requirement dondit rub this 

4. Run FastAPI
From the project root, execute:
"uvicorn backend.main:app --reload" 

The API will run at:

http://127.0.0.1:8000

To test the API, open:

http://127.0.0.1:8000/docs

6. Run the Frontend

"python -m http.server 5500 --directory frontend"

After run open local frontend to try this project 
http://127.0.0.1:5500

