import re
import sys
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
import pdfplumber

@dataclass
class TxnRow:
    proveedor: str
    fecha: str
    numero_factura: Optional[str]
    importe: float
    saldo_final_proveedor: Optional[float] = None


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_number_argentina(num_str: str) -> float:
    """Convierte '1.234.567,89' → 1234567.89"""
    s = num_str.replace(".", "").replace(",", ".")
    return float(re.sub(r"[^0-9\.\-]", "", s))


def is_supplier_line(line: str) -> bool:
    return bool(re.search(r"^Proveedor:\s+", line))


def extract_supplier_name(line: str) -> Optional[str]:
    m = re.search(r"Proveedor:\s+[0-9A-Z]+\s+(.+?)\s+-\s+Cuenta Corriente",
                  line, flags=re.IGNORECASE)
    if m:
        return normalize_spaces(m.group(1))
    m2 = re.search(r"Proveedor:\s+[0-9A-Z]+\s+(.+?)\s+-\s+",
                   line, flags=re.IGNORECASE)
    if m2:
        return normalize_spaces(m2.group(1))
    return None


def line_starts_with_date(line: str) -> bool:
    return bool(re.match(r"^\d{2}/\d{2}/\d{4}\b", line))


def extract_comprobante_code(line: str) -> Optional[str]:
    m = re.match(r"^\d{2}/\d{2}/\d{4}\s+([A-Z]{2,3})\b", line)
    return m.group(1) if m else None


def extract_numbers_in_line(line: str) -> List[str]:
    # números como 1.234,56 o -19.065,34
    return re.findall(r"-?\d{1,3}(?:\.\d{3})*,\d{2}", line)


def extract_factura_number(line: str) -> Optional[str]:
    m = re.search(r"(\d{4,5})\s*[-–]\s*(\d{8})", line)
    return f"{m.group(1)}-{m.group(2)}" if m else None


def parse_pdf(pdf_path: str) -> List[TxnRow]:
    rows: List[TxnRow] = []
    last_saldo_by_supplier: Dict[str, float] = {}
    current_supplier: Optional[str] = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [normalize_spaces(l) for l in text.splitlines()
                     if normalize_spaces(l)]

            for line in lines:
                if is_supplier_line(line):
                    current_supplier = extract_supplier_name(line) or current_supplier
                    continue
                if not current_supplier:
                    continue
                if not line_starts_with_date(line):
                    continue

                comp_code = extract_comprobante_code(line)
                if not comp_code:
                    continue

                nums = extract_numbers_in_line(line)
                if nums:
                    last_saldo_by_supplier[current_supplier] = parse_number_argentina(nums[-1])

                # ignorar OP
                if comp_code == "OP":
                    continue

                if len(nums) >= 2:
                    importe = parse_number_argentina(nums[-2])
                elif len(nums) == 1:
                    importe = abs(parse_number_argentina(nums[0]))
                else:
                    continue

                fecha = re.match(r"^(\d{2}/\d{2}/\d{4})", line).group(1)
                numero_factura = extract_factura_number(line)

                rows.append(
                    TxnRow(
                        proveedor=current_supplier,
                        fecha=fecha,
                        numero_factura=numero_factura,
                        importe=importe,
                        saldo_final_proveedor=last_saldo_by_supplier.get(current_supplier),
                    )
                )

    # rellenar saldo final para cada fila
    for r in rows:
        r.saldo_final_proveedor = last_saldo_by_supplier.get(r.proveedor, None)

    return rows

def convert_pdf_to_excel(pdf_path: Path, out_xlsx: Path) -> None:
    rows = parse_pdf(str(pdf_path))

    df = pd.DataFrame([{
        "Proveedor": r.proveedor,
        "Fecha": r.fecha,
        "Numero de Factura": r.numero_factura,
        "Importe": r.importe,
        "Saldo Final Proveedor": r.saldo_final_proveedor,
    } for r in rows])

    def parse_date_ddmmyyyy(s: str):
        try:
            d, m, y = s.split("/")
            return int(y), int(m), int(d)
        except Exception:
            return (0, 0, 0)

    df["_k"] = df["Fecha"].apply(parse_date_ddmmyyyy)
    df.sort_values(by=["Proveedor", "_k"], inplace=True)
    df.drop(columns=["_k"], inplace=True)

    df.to_excel(out_xlsx, index=False)
