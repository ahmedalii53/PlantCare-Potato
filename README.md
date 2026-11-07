# PlantCare AI — Potato Disease Classification

PlantCare AI is an educational prototype that classifies potato leaf images into three classes:
- `Potato___Early_blight`
- `Potato___Late_blight`
- `Potato___healthy`

The project includes model training and evaluation in a Jupyter Notebook, MLflow experiment tracking with SQLite, a FastAPI backend, and a web frontend.

> **Disclaimer:** This is a capstone/educational prototype, not a substitute for assessment by an agricultural expert.

## 1. Project structure

Expected structure (the exact model artifact path depends on the notebook's export cell and the path configured in `main.py`):

```text
PlantCare_Potato_Project/
├── dataset/
│   └── Potato/
│       ├── Potato___Early_blight/
│       ├── Potato___Late_blight/
│       └── Potato___healthy/
├── notebooks/
│   └── potato_training_mlflow.ipynb
├── main.py
├── class_names.json
├── requirements.txt
├── mlruns/       # May be created by MLflow
├── mlflow.db     # SQLite tracking database, if configured at this path
└── README.md
```

## 2. Requirements

- Python version compatible with the versions in `requirements.txt`
- VS Code (recommended), with Python and Jupyter extensions
- Dataset arranged in the folder structure above

## 3. Open the project

Open `PlantCare_Potato_Project` in VS Code and open a terminal in the project root (the folder containing `requirements.txt` and `main.py`).

## 4. Create and activate a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If activation is blocked in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

## 5. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check that your active Python version is compatible with the pinned package versions if installation fails.

## 6. Train and evaluate the models

1. Open `notebooks/potato_training_mlflow.ipynb`.
2. Select the Python interpreter from `.venv`.
3. Confirm that the dataset path points to `dataset/Potato`.
4. Run the notebook cells in order, or select **Run All**.
5. Wait for data preparation, training, evaluation, and model-export cells to finish.

The notebook exports the trained model artifact. FastAPI loads the saved artifact for inference. Training can take time depending on the architectures, epochs, and available hardware. You do not need to retrain every time you launch the application if the model artifact already exists.

## 7. MLflow tracking with SQLite

The notebook uses MLflow to track experiment runs. With SQLite, tracking metadata is saved in a database file, commonly `mlflow.db`. The exact path is determined by the notebook's `mlflow.set_tracking_uri(...)` configuration.

Open a **separate terminal** in the project root, activate `.venv`, and run:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Open:

```text
http://127.0.0.1:5000
```

If the notebook configures SQLite at another path, use that same path in the UI command. The notebook and MLflow UI must point to the same database.

## 8. Run FastAPI

Ensure the exported model and `class_names.json` are present at the paths expected by `main.py`. From the project root, activate `.venv` and run:

```bash
uvicorn main:app --reload
```

The API is typically available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Use Swagger to inspect the implemented endpoints and test image prediction. If `main.py` is in a different folder or package, adjust the Uvicorn import path accordingly.

## 9. Run the frontend

For a static HTML/CSS/JavaScript frontend:

1. Open the frontend folder in VS Code.
2. Start **Live Server** on its `index.html`.
3. Open the local address displayed by Live Server (often `http://127.0.0.1:5500`).
4. Confirm that the frontend's API URL points to the running FastAPI backend, usually `http://127.0.0.1:8000`.
5. Upload a potato leaf image and click **Analyze**.

Keep the FastAPI terminal running while using the frontend.

## 10. Recommended startup order (after training)

1. Open the project in VS Code.
2. Activate `.venv`.
3. Start FastAPI:

   ```bash
   uvicorn main:app --reload
   ```

4. Start the frontend with Live Server.
5. Open the frontend in your browser and upload an image.
6. Optionally, start MLflow UI in another terminal:

   ```bash
   mlflow ui --backend-store-uri sqlite:///mlflow.db
   ```

## 11. Troubleshooting

### `ModuleNotFoundError`
Activate `.venv` and run `pip install -r requirements.txt`.

### Model file not found
Run the notebook's model export/save cell and confirm the artifact path matches the path configured in `main.py`.

### Dataset not found
Confirm the dataset is located at `dataset/Potato/` and that the class folder names match those listed above.

### Frontend cannot connect to FastAPI
- Confirm FastAPI is running.
- Check the API URL configured in the frontend.
- Check the browser console and backend terminal for errors.
- Confirm FastAPI's CORS configuration allows the frontend's local origin.

### MLflow UI does not show runs
- Confirm the notebook and UI use the same SQLite database path.
- Confirm the notebook completed the MLflow logging cells.
- Start MLflow UI with the correct `--backend-store-uri`.

## 12. Notes

- Keep the exported model artifact if you want to run inference without retraining.
- The dataset may not be included in the project package because of its size; place it in `dataset/Potato/` before running the notebook.
- MLflow stores experiment tracking metadata; the model used by FastAPI is exported separately by the notebook.
- Model predictions and confidence scores are not guaranteed diagnoses.
