# Capturing Radiance in Genshin Impact

A quick toolkit to turn your wish-log Excel into insights and predictions for the “Capturing Radiance” mechanic.

## Quick Start

1. **Clone** this repo and `cd` into it.  
2. **Install** dependencies:
   ```bash
   pip install -r requirements.txt

   data_loader.py - read & clean Excel → DataFrame/SQLite
	•	eda_single.py - summary stats + pity histogram + cost scatter
	•	model_training.py - XGBoost classifier/regressor training
	•	predict_console.py - real-time next-Radiance chance & cost
	•	requirements.txt - all necessary Python packages
	•	data/ - put your .xlsx logs her
   **Removed Components**  
`streamlit_app.py` has been **removed** in favor of the lightweight console-based predictor (`predict_console.py`).  
If you need a web dashboard in the future, feel free to reintroduce a Streamlit or Flask app in a separate branch.

