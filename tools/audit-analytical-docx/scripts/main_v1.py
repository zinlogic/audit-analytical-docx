import sys
import os
import argparse
import math
import re
from extractors import extract_summary_data, extract_chromatogram_data
from markdown_pdf import MarkdownPdf, Section

PDF_CSS = """
body {
    margin: 0;
}
table {
    border-collapse: collapse;
    margin-left: 0;
    width: 100%;
}
th,
td {
    padding: 2pt 8pt 2pt 0;
    text-align: left;
    vertical-align: top;
}
th:first-child,
td:first-child {
    padding-left: 0;
}
"""

def build_default_output_path(tabla_path: str) -> str:
    base_name = os.path.basename(tabla_path).replace(".docx", "").replace(".doc", "")
    suffix = re.sub(r"^Tabla\s+", "", base_name, flags=re.IGNORECASE)
    safe_suffix = re.sub(r"[^A-Za-z0-9_. -]+", "_", suffix).strip() or "reporte"

    output_dir = os.path.dirname(os.path.abspath(tabla_path)) or os.getcwd()
    return os.path.join(output_dir, f"reporte_auditoria_v1_{safe_suffix}.md")

def check_match(val1: str, val2: str) -> bool:
    """
    Compara dos valores. Primero intenta coincidencia exacta de texto.
    Si falla, intenta convertirlos a float y verificar si son numéricamente cercanos
    para manejar notación científica vs decimal (ej. '8.731e+05' vs '873100').
    """
    if val1 == val2:
        return True
    
    try:
        f1 = float(val1)
        f2 = float(val2)
        # Usamos tolerancia relativa para manejar pequeñas diferencias de punto flotante
        return math.isclose(f1, f2, rel_tol=1e-4)
    except ValueError:
        return False

def generate_report(summary_data, details_data) -> str:
    summary_samples = summary_data.get("samples", [])
    sum_metadata = summary_data.get("metadata", {})
    total_samples = min(len(summary_samples), len(details_data))
    
    errores = []
    muestras_con_error = set()
    
    for i in range(total_samples):
        sum_sample = summary_samples[i]
        det_sample = details_data[i]
        
        s_id = sum_sample.get("id", i + 1)
        s_name = sum_sample.get("Sample Name", "")
        
        campos_a_verificar = [
            {
                "campo": "Sample Name",
                "val_resumen": sum_sample.get("Sample Name", ""),
                "val_detalle": det_sample.get("metadata", {}).get("Sample Name", "")
            },
            {
                "campo": "Sample Type",
                "val_resumen": sum_sample.get("Sample Type", ""),
                "val_detalle": det_sample.get("metadata", {}).get("Sample Type", "")
            },
            {
                "campo": "Acquisition Date",
                "val_resumen": sum_sample.get("Acquisition Date", ""),
                "val_detalle": det_sample.get("metadata", {}).get("Acquisition Date", "")
            },
            {
                "campo": "Area (cps)",
                "val_resumen": sum_sample.get("Area (cps)", ""),
                "val_detalle": det_sample.get("results", {}).get("Target Analyte", {}).get("Area (cps)", "")
            },
            {
                "campo": "IS Area (cps)",
                "val_resumen": sum_sample.get("IS Area (cps)", ""),
                "val_detalle": det_sample.get("results", {}).get("Internal Standard", {}).get("Area (cps)", "")
            },
            {
                "campo": "RT (min)",
                "val_resumen": sum_sample.get("RT (min)", ""),
                "val_detalle": det_sample.get("results", {}).get("Target Analyte", {}).get("RT (min)", "")
            },
            {
                "campo": "Calculated Conc. (ng/mL)",
                "val_resumen": sum_sample.get("Calculated Conc. (ng/mL)", ""),
                "val_detalle": det_sample.get("results", {}).get("Target Analyte", {}).get("Calc. Conc. (ng/mL)", "")
            },
            {
                "campo": "Acquisition Method",
                "val_resumen": sum_metadata.get("Acquisition Method", ""),
                "val_detalle": det_sample.get("metadata", {}).get("Acquisition Method", "")
            },
            {
                "campo": "Project",
                "val_resumen": sum_metadata.get("Project", ""),
                "val_detalle": det_sample.get("metadata", {}).get("Project", "")
            },
            {
                "campo": "Instrument",
                "val_resumen": sum_metadata.get("Instrument", ""),
                "val_detalle": det_sample.get("metadata", {}).get("Instrument Name", "")
            }
        ]
        
        for item in campos_a_verificar:
            campo = item["campo"]
            v_res = item["val_resumen"]
            v_det = item["val_detalle"]
            
            estado = "✅ OK" if check_match(v_res, v_det) else "❌ ERROR"
            
            if estado == "❌ ERROR":
                muestras_con_error.add(s_id)
                errores.append(f"- **ID {s_id} ({s_name})**: El campo '{campo}' difiere. Tabla: `{v_res}` vs Cromatograma: `{v_det}`")
                
    total_errores = len(muestras_con_error)
    total_ok = total_samples - total_errores

    analyte_info = summary_data.get("analyte", "")

    md_report = "### Resumen de Auditoría\n"
    if analyte_info:
        md_report += f"- **{analyte_info}**\n"
    md_report += f"- **Muestras Totales Analizadas:** {total_samples}\n"
    md_report += f"- **Muestras Sin Errores:** {total_ok}\n"
    md_report += f"- **Muestras Con Errores:** {total_errores}\n\n"

    md_report += "### Correspondencia de Variables\n"
    md_report += "| Campo Lógico | Ubicación en Archivo Tabla | Ubicación en Archivo Cromatograma |\n"
    md_report += "|---|---|---|\n"
    md_report += "| **Sample Name** | Columna 'Sample Name' | Metadatos de la Inyección: 'Sample Name' |\n"
    md_report += "| **Sample Type** | Columna 'Sample Type' | Metadatos de la Inyección: 'Sample Type' |\n"
    md_report += "| **Acquisition Date** | Columna 'Acquisition Date' | Metadatos de la Inyección: 'Acquisition Date' |\n"
    md_report += "| **Area (cps)** | Columna 'Area (cps)' | Tabla Target Analyte: 'Area (cps)' |\n"
    md_report += "| **IS Area (cps)** | Columna 'IS Area (cps)' | Tabla Internal Standard: 'Area (cps)' |\n"
    md_report += "| **RT (min)** | Columna 'RT (min)' | Tabla Target Analyte: 'RT (min)' |\n"
    md_report += "| **Calculated Conc.** | Columna 'Calculated Conc. (ng/mL)' | Tabla Target Analyte: 'Calc. Conc. (ng/mL)' |\n"
    md_report += "| **Acquisition Method** | Metadatos Globales: 'Acquisition Method' | Metadatos de la Inyección: 'Acquisition Method' |\n"
    md_report += "| **Project** | Metadatos Globales: 'Project' | Metadatos de la Inyección: 'Project' |\n"
    md_report += "| **Instrument** | Metadatos Globales: 'Instrument' | Metadatos de la Inyección: 'Instrument Name' |\n\n"

    md_report += "### Detalle de Errores Encontrados\n"
    if errores:
        md_report += f"❌ **Se encontraron {len(errores)} inconsistencias en {total_errores} muestras:**\n\n"
        md_report += "\n".join(errores) + "\n\n"
    else:
        md_report += "✅ No se encontraron inconsistencias. Todos los datos coinciden perfectamente.\n\n"
            
    return md_report

def main():
    parser = argparse.ArgumentParser(description="Auditoría Analítica Pura (Sin LLM)")
    parser.add_argument("--tabla", default="datos/Tabla Secuencia 1-RE-EZPC.docx", help="Ruta al archivo de Tabla")
    parser.add_argument("--cromatograma", default="datos/Cromatogramas Secuencia 1-RE-EZPC.docx", help="Ruta al archivo de Cromatogramas")
    parser.add_argument("--output", default="", help="Ruta para guardar el reporte final. Si se omite, se guarda junto al archivo de tabla.")
    
    args = parser.parse_args()
    
    if not args.output:
        args.output = build_default_output_path(args.tabla)
        output_mode = "directorio de los DOCX"
    else:
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        output_mode = "permanente"
    
    if not os.path.exists(args.tabla):
        print(f"Error: No se encontró el archivo de tabla en {args.tabla}")
        sys.exit(1)
        
    if not os.path.exists(args.cromatograma):
        print(f"Error: No se encontró el archivo de cromatograma en {args.cromatograma}")
        sys.exit(1)
        
    print(f"Iniciando auditoría (Modo Código Puro)...")
    print(f"Tabla: {args.tabla}")
    print(f"Cromatograma: {args.cromatograma}")
    print(f"Salida: {args.output} ({output_mode})")
    print("-" * 40)
    
    try:
        summary_data = extract_summary_data(args.tabla)
        details_data = extract_chromatogram_data(args.cromatograma)
        
        report = generate_report(summary_data, details_data)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
            
        pdf_output = os.path.splitext(args.output)[0] + ".pdf"
        try:
            pdf = MarkdownPdf(toc_level=0)
            pdf.add_section(Section(report), user_css=PDF_CSS)
            pdf.save(pdf_output)
            pdf_msg = f" y {pdf_output}"
        except Exception as pdf_e:
            pdf_msg = f" (Error generando PDF: {pdf_e})"
            
        print("-" * 40)
        print(f"Auditoría finalizada. Reporte guardado en {args.output}{pdf_msg}")
        
    except Exception as e:
        print(f"Ocurrió un error durante la extracción o generación del reporte: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
