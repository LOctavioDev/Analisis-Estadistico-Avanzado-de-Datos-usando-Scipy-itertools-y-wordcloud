# === Librerías básicas ===
from gc import collect
from warnings import filterwarnings
import re
import numpy as np
import pandas as pd
from scipy import stats
from itertools import cycle, combinations
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import ListedColormap
import seaborn as sns
from wordcloud import WordCloud
import webbrowser
import os

filterwarnings('ignore')
collect()

class color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# === Funciones ===

def plot_missing_values_heatmap(df):
    """
    Muestra un heatmap de los valores nulos por columna con conteo,
    usando anotaciones y escala de color.
    """
    missing_counts = df.isnull().sum().to_frame().T
    missing_counts = missing_counts.loc[:, (missing_counts != 0).any(axis=0)]

    if missing_counts.empty:
        print(f"{color.GREEN}No missing values to plot!{color.END}")
        return

    plt.figure(figsize=(14, 1.5))
    sns.heatmap(
        missing_counts, annot=True, fmt='d', cmap='coolwarm',
        cbar_kws={"orientation": "horizontal", "label": "Count of missing values"}
    )
    plt.title("Missing Values per Column", fontsize=14)
    plt.yticks([], [])
    plt.tight_layout()
    plt.savefig("missing_heatmap.png")
    print(f"{color.GREEN} Heatmap image saved as 'missing_heatmap.png'.{color.END}")
    webbrowser.open(f"file://{os.path.abspath('missing_heatmap.png')}")
    plt.show()


def show_dataframe_html(df, filename="tabla.html"):
    """Guarda un DataFrame como HTML y lo abre en el navegador."""
    df.to_html(filename)
    webbrowser.open(f"file://{os.path.abspath(filename)}")


def generate_full_statistics_report(df, filename="reporte_estadistico.html"):
    """
    Genera un archivo HTML con estadísticas avanzadas + resumen de variables.
    Todo en una sola página bien estructurada.
    """
    numeric_df = df.select_dtypes(include=[np.number])

    stats = {
        "Mean": numeric_df.mean(),
        "Median": numeric_df.median(),
        "Mode": numeric_df.mode().iloc[0],
        "Range": numeric_df.max() - numeric_df.min(),
        "Stdev": numeric_df.std(),
        "Variance": numeric_df.var(),
        "IQR": numeric_df.quantile(0.75) - numeric_df.quantile(0.25),
        "25%": numeric_df.quantile(0.25),
        "50%": numeric_df.quantile(0.50),
        "75%": numeric_df.quantile(0.75),
        "Min": numeric_df.min(),
        "Max": numeric_df.max(),
        "Skewness": numeric_df.skew(),
        "Kurtosis": numeric_df.kurt()
    }

    stats_df = pd.DataFrame(stats).T.round(2)
    stats_df.index.name = "Metric"

    summary_df = pd.DataFrame({
        "Variable": df.columns,
        "Dtype": df.dtypes.values,
        "Count": df.count().values,
        "Unique": df.nunique().values,
        "Missing": df.isnull().sum().values
    })

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"<h1>Resumen Estadistico Avanzado</h1>\n")
        f.write(stats_df.to_html(border=1, classes="stats-table"))
        f.write("<br><hr><br>\n")
        f.write(f"<h2>Resumen de Variables</h2>\n")
        f.write(summary_df.to_html(index=False, border=1, classes="summary-table"))

    webbrowser.open(f"file://{os.path.abspath(filename)}")

    print(f"{color.GREEN}✔ Reporte estadístico completo exportado a '{filename}' y abierto en el navegador.{color.END}")

    return stats_df, summary_df


# === Configuración visual ===
plt.style.use("fivethirtyeight")
sns.set(rc={"figure.figsize": (10, 10)})

print(f"{color.GREEN} Successfully configured libraries!{color.END}")

# === Cargar dataset ===
try:
    df = pd.read_csv('data/datos_actualizados.csv')
    print(f"{color.GREEN} Dataset loaded successfully.{color.END}")
    print("\n--- DataFrame Info ---")
    print(df.info())
    print("\n--- DataFrame Head ---")
    print(df.head())
    print("\n--- DataFrame Describe ---")
    print(df.describe(include='all'))
except FileNotFoundError:
    print(f"{color.RED}✘ Error: File not found. Check the file path.{color.END}")
    df = None
except Exception as e:
    print(f"{color.RED}✘ An error occurred: {e}{color.END}")
    df = None

# === Análisis si se cargó el DataFrame ===
if df is not None:
    print(color.BLUE)
    collect()

    # Heatmap de nulos
    plot_missing_values_heatmap(df)

    # Duplicados
    duplicate_values = df.duplicated().sum()
    print(f"{color.BLUE}→ The data contains {color.BOLD}{color.RED}{duplicate_values}{color.END}{color.BLUE} duplicate rows.{color.END}")

    df_no_duplicates = df.drop_duplicates()

    # Guardar tabla limpia
    df_no_duplicates.to_csv("data/clean_data.csv", index=False)
    print(f"{color.GREEN}✔ Duplicate rows removed and clean data saved to 'clean_data.csv'.{color.END}")

    # Mostrar tabla HTML
    show_dataframe_html(df_no_duplicates)

    # Estadísticas + resumen de variables (en 1 HTML)
    stats_df, summary_df = generate_full_statistics_report(df_no_duplicates)

    # Mostrar duplicados en tabla si existen
    if duplicate_values > 0:
        duplicated_rows = df[df.duplicated()]
        show_dataframe_html(duplicated_rows, filename="duplicados.html")
        print(f"{color.YELLOW}✔ Duplicate rows exported to 'duplicados.html'.{color.END}")
