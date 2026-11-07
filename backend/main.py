from pathlib import Path
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "plant_model.keras"
CLASS_PATH = BASE_DIR / "models" / "class_names.json"
IMAGE_SIZE = 256

app = FastAPI(title="PlantCare Potato API", version="1.0.0",
              description="Potato leaf disease classification with Grad-CAM visual explanation.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

model = None
class_names = []

@app.on_event("startup")
def load_model():
    global model, class_names
    if MODEL_PATH.exists() and CLASS_PATH.exists():
        model = tf.keras.models.load_model(MODEL_PATH)
        class_names = json.loads(CLASS_PATH.read_text(encoding="utf-8"))

@app.get("/")
def root():
    return {"message": "PlantCare Potato API", "model_loaded": model is not None,
            "classes": class_names, "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

def read_image(file_bytes):
    try:
        img = Image.open(BytesIO(file_bytes)).convert("RGB")
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE))
        return np.array(img, dtype=np.float32)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {exc}")

def find_last_conv(layer):
    # Search nested models too (MobileNet/EfficientNet feature extractor).
    for sublayer in reversed(layer.layers):
        if isinstance(sublayer, tf.keras.layers.Conv2D):
            return sublayer
        if isinstance(sublayer, tf.keras.Model):
            found = find_last_conv(sublayer)
            if found is not None:
                return found
    return None

def make_gradcam(img_array, predicted_index):
    """
    Grad-CAM heatmap from the selected model's final convolutional layer.
    Returns None when a selected architecture's graph cannot expose the layer
    cleanly; prediction remains available.
    """
    try:
        conv_layer = find_last_conv(model)
        if conv_layer is None:
            return None
        grad_model = tf.keras.Model(
            inputs=model.inputs,
            outputs=[conv_layer.output, model.output]
            )
        input_tensor = tf.convert_to_tensor(np.expand_dims(img_array, 0))
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(input_tensor, training=False)
            score = predictions[:, predicted_index]
        grads = tape.gradient(score, conv_outputs)
        if grads is None:
            return None
        weights = tf.reduce_mean(grads, axis=(1, 2))
        cam = tf.reduce_sum(weights[:, tf.newaxis, tf.newaxis, :] * conv_outputs, axis=-1)
        cam = tf.nn.relu(cam)[0]
        max_value = tf.reduce_max(cam)
        if float(max_value) <= 0:
            return None
        cam = cam / max_value
        cam = tf.image.resize(cam[..., tf.newaxis], (IMAGE_SIZE, IMAGE_SIZE)).numpy().squeeze()
        return cam
    except Exception as exc:
        print("Grad-CAM could not be generated:", repr(exc))
        return None

def overlay_heatmap(img_array, heatmap):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import cm
    heat_rgb = (cm.jet(heatmap)[..., :3] * 255).astype(np.uint8)
    base = img_array.astype(np.uint8)
    overlay = (0.55 * base + 0.45 * heat_rgb).clip(0, 255).astype(np.uint8)
    buffer = BytesIO()
    Image.fromarray(overlay).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not found. Run the training notebook first.")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")
    contents = await file.read()
    if len(contents) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image is too large. Maximum size is 12 MB.")
    img_array = read_image(contents)
    scores = model.predict(np.expand_dims(img_array, 0), verbose=0)[0]
    pred_index = int(np.argmax(scores))
    pred_class = class_names[pred_index]
    confidence = float(scores[pred_index])
    heatmap = make_gradcam(img_array, pred_index)
    explanation = overlay_heatmap(img_array, heatmap) if heatmap is not None else None
    return {
        "predicted_class": pred_class,
        "confidence": confidence,
        "probabilities": {class_names[i]: float(scores[i]) for i in range(len(class_names))},
        "gradcam_overlay": explanation,
        "explanation_available": explanation is not None,
        "note": "Confidence is the model's score, not a guarantee. Grad-CAM is an approximate visual explanation."
    }
