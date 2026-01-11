from fastapi import APIRouter, UploadFile, Depends
from pathlib import Path
import shutil
from fastapiprob.pdf_service import convert_pdf_to_excel
from fastapi.responses import FileResponse
from sqlmodel import Session
from fastapiprob.database import get_session
from fastapiprob.models import Document

router = APIRouter()

@router.post("/documents/upload")
async def upload_file(file: UploadFile, session: Session = Depends(get_session)):
    pdf_path = Path("data/pdf") / file.filename #operator "/" overloaded by pathlib.Path
    excel_path = Path("data/excel") / (pdf_path.stem + ".xlsx")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file.file.close()
    convert_pdf_to_excel(pdf_path, excel_path)

    document = Document(
        user_id=1,  #temporary
        pdf_name=file.filename,
        pdf_path=str(pdf_path),
        excel_name=excel_path.name,
        excel_path=str(excel_path),
    )

    session.add(document)
    session.commit()

    return FileResponse(
        path=excel_path,
        filename=excel_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
