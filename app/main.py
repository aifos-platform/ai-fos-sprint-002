from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import ImportJob, Organisation
from app.schemas import ImportCreate, ImportRead, OrganisationCreate, OrganisationRead


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Digital CFO platform canonical data foundation",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": "0.2.0"}


@app.post("/organisations", response_model=OrganisationRead, status_code=status.HTTP_201_CREATED)
def create_organisation(payload: OrganisationCreate, db: Session = Depends(get_db)) -> Organisation:
    organisation = Organisation(
        name=payload.name.strip(),
        base_currency=payload.base_currency.upper(),
        fiscal_year_start_month=payload.fiscal_year_start_month,
    )
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


@app.get("/organisations/{organisation_id}", response_model=OrganisationRead)
def get_organisation(organisation_id: str, db: Session = Depends(get_db)) -> Organisation:
    organisation = db.get(Organisation, organisation_id)
    if organisation is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return organisation


@app.post(
    "/organisations/{organisation_id}/imports",
    response_model=ImportRead,
    status_code=status.HTTP_201_CREATED,
)
def register_import(
    organisation_id: str,
    payload: ImportCreate,
    db: Session = Depends(get_db),
) -> ImportJob:
    organisation = db.get(Organisation, organisation_id)
    if organisation is None:
        raise HTTPException(status_code=404, detail="Organisation not found")

    import_job = ImportJob(
        organisation_id=organisation_id,
        source_filename=payload.source_filename,
        source_system=payload.source_system,
    )
    db.add(import_job)
    db.commit()
    db.refresh(import_job)
    return import_job


@app.get("/imports/{import_id}", response_model=ImportRead)
def get_import(import_id: str, db: Session = Depends(get_db)) -> ImportJob:
    import_job = db.get(ImportJob, import_id)
    if import_job is None:
        raise HTTPException(status_code=404, detail="Import job not found")
    return import_job
