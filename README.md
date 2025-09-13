# 🛡️ BiasShield – Bias-Free Firewall  

BiasShield is a smart bias-detection firewall designed to catch and prevent unintentional bias in hiring filters, recruitment platforms, or automated decision-making systems. It combines **rule-based detection** with **NLP/ML models** to ensure fairness in candidate screening.  



## 🚀 Features  

- ✅ **Rule-Based Scanning** – Detects obvious biased filters (e.g., "Only males allowed", "Age < 30 only").  
- 🤖 **NLP + ML Analysis** – Flags hidden/unintentional biases in job descriptions or filters using AI models.  
- 🔄 **Hybrid Approach** – Combines strict keyword rules with intelligent AI-based context scanning.  
- 🌐 **REST API** – Exposes an `/api/predict` endpoint to check any hiring request/filter.  
- 🧑‍💻 **Human-in-the-Loop** – Suspicious cases are flagged for human review instead of auto-blocking.  



## 📂 Project Structure  

```sh
Project/
│── .idea/
│   ├── inspectionProfiles/
│   ├── firewall.iml
│   ├── misc.xml
│   ├── modules.xml
│
│── static/
│   └── (static files go here, e.g., images, CSS, JS)
│
│── .gitignore
│── README.md
│── bias_model_pipeline.pkl
│── firewall.py


```


## 🧠 How it Works

- Rule-Based Check : Looks for predefined biased terms (gender, age, religion, etc.).
- NLP/ML Check : Uses AI models to detect contextual or hidden biases.
- Firewall Decision : Approves, flags, or sends for human review.


## 🛠 Tech Stack

- Python + Flask – Backend & API
- Transformers (Hugging Face) – NLP models
- scikit-learn – Machine learning models
- HTML/CSS/JS – Simple UI


## 🤝 Contributing

Contributions are welcome!
Fork the repo, make your changes, and open a Pull Request 
