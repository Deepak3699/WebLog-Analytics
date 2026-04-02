# 📊 Web Log Analyzer

ML-powered web log analysis with anomaly detection and pattern discovery.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Data
Place your log file in:
```
data/raw/finalweblog.txt
```

### 3. Train Model
Open and run all cells in:
```bash
jupyter notebook notebooks/preprocessing.ipynb
```

### 4. Run Web App
```bash
cd app
uvicorn main:app --reload
```

Open browser: **http://localhost:8000**

---

## 📂 Project Structure
```
WEBLOG/
├── data/raw/              # Put your log files here
├── models/                # Trained model saved here
├── notebooks/             # Training notebook
├── app/                   # Web application
│   ├── main.py
│   └── templates/
└── src/                   # Pattern analysis scripts
```

---

## 🎯 Features
- ✅ Upload any web log file
- ✅ Detect anomalies automatically
- ✅ Discover traffic patterns
- ✅ Identify potential attacks
- ✅ View visualizations

---

## 📖 Usage

### Upload & Analyze
1. Click **"Choose File"**
2. Select your `.txt` log file
3. View instant analysis results

### Run Pattern Discovery (Optional)
```bash
python src/pattern_discovery.py
python src/pattern_visualizer.py
```

---

## 📦 Requirements
- Python 3.8+
- FastAPI
- Pandas
- Scikit-learn
- Matplotlib

---

## 🆘 Troubleshooting

**Model not found?**
→ Run the notebook first to train the model

**Upload fails?**
→ Check log file format matches Apache/Nginx common log format

**Port already in use?**
→ Use: `uvicorn main:app --port 8001`

---

**Done!** 🎉
