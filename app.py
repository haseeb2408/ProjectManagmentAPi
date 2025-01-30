from flask import Flask ,render_template , request , jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from api import GEMINI_API_KEY
import os
import json





app = Flask(__name__ , template_folder='templates')
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
llm = ChatGoogleGenerativeAI(model = "gemini-pro" , api_key = GEMINI_API_KEY)






@app.route('/pdfreader' , methods = ['POST'])
def pdfreader():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"})

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            extracted_text = "\n".join([page.page_content for page in pages])
            prompt = f'''
            I have loaded a Project file in pdf its content is .

            ### Data:
            "{extracted_text}"

            **Instructions:**
            1. Read the content carefully.
            2. Divide the content into easy-to-understand, bite-sized tasks and subtasks.
            3. Each task should have a **unique ID**, a **title**, and a **description**.
            4. The description should explain the task in **simple, step-wise terms**.
            5. Return the response in **valid JSON String**, structured like this without empty space and line:
            [ {{"id": "1", "title": "Task Title", "Description": "Task Description in simple words"}}, {{"id": "2", "title": "Another Task", "Description": "Another Task Description"}} ]'''
            response = llm.invoke(prompt)
            json_data = json.loads(response.content)
            return jsonify(json_data)


if __name__ == '__main__':
    app.run(debug= True)