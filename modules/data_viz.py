import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid

class DataAnalyzer:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def get_csv_columns(self, filename):
        """Kay7ll l'fichier w kayrje3 lina smiyat l'colonnes"""
        filepath = os.path.join(self.upload_folder, filename)
        try:
            df = pd.read_csv(filepath)
            # Kanferzo columns: Ar9am bohdhom, w Text bohdo
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            all_cols = df.columns.tolist()
            preview = df.head().to_html(classes='table table-sm', index=False) # Preview sghir
            return {
                "numeric": numeric_cols,
                "all": all_cols,
                "preview": preview,
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_custom_chart(self, filename, chart_type, x_col, y_col, output_folder):
        """Kayrasm graph 3la hsab khtiyar l'user"""
        filepath = os.path.join(self.upload_folder, filename)
        df = pd.read_csv(filepath)
        
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")

        # Logic dyal Rasm
        if chart_type == 'bar':
            sns.barplot(data=df, x=x_col, y=y_col, palette="viridis")
            plt.title(f"{y_col} by {x_col} (Bar Chart)")

        elif chart_type == 'line':
            sns.lineplot(data=df, x=x_col, y=y_col, marker='o', color='teal')
            plt.title(f"Trend of {y_col} over {x_col}")

        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x=x_col, y=y_col, hue=y_col, palette="cool", s=100)
            plt.title(f"Correlation: {x_col} vs {y_col}")

        elif chart_type == 'donut':
            # Donut Chart khasso traitement special
            data = df.groupby(x_col)[y_col].sum()
            plt.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
            # Nzid دائرة (circle) f lwsst bach twli Donut
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            plt.title(f"Distribution of {y_col} by {x_col}")

        # Sauvegarde
        filename = f"chart_{uuid.uuid4().hex}.png"
        filepath = os.path.join(output_folder, filename)
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()
        
        return filename