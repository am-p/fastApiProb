from fastapi import APIRouter, UploadFile
from pathlib import Path
import shutil
from fastapiprob.pdf_service import convert_pdf_to_excel

router = APIRouter()

@router.post("/documents/upload")
async def upload_file(file: UploadFile):
    pdf_path = Path("data/pdf") / file.filename #operator "/" overloaded by pathlib.Path
    excel_path = Path("data/excel") / (pdf_path.stem + ".xlsx")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file.file.close()
    convert_pdf_to_excel(pdf_path, excel_path)

    return {
        "pdf": str(pdf_path),
        "excel": str(excel_path),
    }    
