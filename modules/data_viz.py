import pandas as pd
import os
import numpy as np

class DataAnalyzer:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def process_and_suggest(self, filename):
        filepath = os.path.join(self.upload_folder, filename)
        
        try:
            # --- 1. SMART READ (Encoding & Separator) ---
           
            try:
                df = pd.read_csv(filepath, sep=None, engine='python', encoding='utf-8')
            except UnicodeDecodeError:
               
                df = pd.read_csv(filepath, sep=None, engine='python', encoding='latin-1')
            
            # --- 2. CLEANING (Nettoyage Intelligent) ---
            
            df = df.dropna(how='all')
            
            # BLOCK: Gestion dyal NaNs (Valeurs Manquantes)
            
            df = df.replace({np.nan: None}) 
            
            # --- 3. DETECT TYPES ---
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            date_cols = []
            for col in cat_cols:
               
                try:
                    # check if > 80% of non-null values are dates
                    sample = df[col].dropna().head(100)
                    if len(sample) > 0:
                        converted = pd.to_datetime(sample, errors='coerce')
                        if converted.notna().sum() > (len(sample) * 0.8):
                            date_cols.append(col)
                            # Convertir column kamla l datetime bach nsta3mloha mn b3d
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
            
            # Update cat_cols 
            cat_cols = [c for c in cat_cols if c not in date_cols]

            # --- 4. GENERATE SUGGESTIONS ---
            suggestions = []
            
            # Line / Area Chart (Time Series)
            if len(date_cols) > 0 and len(num_cols) > 0:
                suggestions.append({
                    "type": "line",
                    "x": date_cols[0],
                    "y": num_cols[0],
                    "title": f"Evolution of {num_cols[0]} over Time"
                })

            # Bar Chart (Comparison)
            if len(cat_cols) > 0 and len(num_cols) > 0:
                suggestions.append({
                    "type": "bar",
                    "x": cat_cols[0],
                    "y": num_cols[0],
                    "title": f"Comparison of {num_cols[0]} by {cat_cols[0]}"
                })
                
                # Pie Chart 
                unique_vals = df[cat_cols[0]].nunique()
                if unique_vals <= 10:
                    suggestions.append({
                        "type": "pie",
                        "labels": cat_cols[0],
                        "values": num_cols[0],
                        "title": f"Distribution of {num_cols[0]}"
                    })

            # Scatter (Correlation)
            if len(num_cols) >= 2:
                suggestions.append({
                    "type": "scatter",
                    "x": num_cols[0],
                    "y": num_cols[1],
                    "title": f"Correlation: {num_cols[0]} vs {num_cols[1]}"
                })

            # --- 5. PREPARE DATA FOR JSON ---
            # Convert dates back to string for JSON serialization
            for dc in date_cols:
                df[dc] = df[dc].astype(str)
            
            # Limit rows to 500 for performance
            chart_data = df.head(500).to_dict(orient='records')

            return {
                "success": True,
                "data": chart_data,
                "suggestions": suggestions,
                "meta": {
                    "rows": len(df),
                    "columns": df.columns.tolist(),
                    "numeric_cols": num_cols,
                    "category_cols": cat_cols,
                    "date_cols": date_cols,
                    "preview_rows": chart_data[:5]
                }
            }

        except Exception as e:
            
            return {"success": False, "error": f"Error processing file: {str(e)}"}
