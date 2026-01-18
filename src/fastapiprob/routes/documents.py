from fastapi import APIRouter, UploadFile, Depends
from pathlib import Path
import shutil
from fastapiprob.pdf_service import convert_pdf_to_excel
from fastapi.responses import FileResponse
from sqlmodel import Session
from fastapiprob.database import get_session
from fastapiprob.models import Document
from fastapiprob.routes.auth import get_current_user
from fastapiprob.models import User

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_file(file: UploadFile,
                      session: Session = Depends(get_session),
                      user: User = Depends(get_current_user)
                      ):
    
    pdf_path = Path("data/pdf") / file.filename #operator "/" overloaded by pathlib.Path
    excel_path = Path("data/excel") / (pdf_path.stem + ".xlsx")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file.file.close()
    convert_pdf_to_excel(pdf_path, excel_path)

    document = Document(
        user_id=user.id,
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
