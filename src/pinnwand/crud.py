from datetime import datetime
import logging
from typing import NamedTuple

import tornado
from sqlalchemy.orm.session import Session

from pinnwand import configuration, database, utility
from pinnwand.error import ValidationError

class PastedFile(NamedTuple):
    lexer: str
    content: str
    filename: str | None

class PasteResult(NamedTuple):
    paste_slug: str
    removal_slug: str

log = logging.getLogger(__name__)

def create_paste(session, files: list[PastedFile], expiry: str | int, auto_scale: bool, source: str) -> PasteResult:
    if len(files) == 0:
        raise ValidationError("No files provided")
    
    if isinstance(expiry, str):
        try:
            expiry_seconds = configuration.expiries[expiry]
        except KeyError:
            log.info("Paste.post: a paste was submitted with an invalid expiry")
            raise ValidationError(f"Invalid expiry {expiry!r}. Allowed values are {tuple(configuration.expiries.keys())!r}.")
    else:
        expiry_seconds = expiry
    
    with utility.SlugContext(auto_scale) as slug_context:
        paste = database.Paste(
            next(slug_context),
            expiry_seconds,
            source,
        )

        # TODO: add test for total_size check
        total_size = 0
        for file in files:        
            db_file = database.File(
                next(slug_context),
                file.content,
                file.lexer,
                file.filename,
            )

            total_size += len(db_file.fmt)
            if total_size > configuration.paste_size:
                raise ValidationError(
                    "Sum of file sizes exceeds size limit when syntax highlighting applied "
                    f"({total_size//1024}kB > {configuration.paste_size//1024}kB)"
                )

            paste.files.append(db_file)

    # For the first file we will always use the same slug as the paste,
    # since slugs are generated to be unique over both pastes and files
    # this can be done safely.
    paste.files[0].slug = paste.slug

    session.add(paste)
    session.commit()

    return PasteResult(paste.slug, paste.removal)

def error_if_expired_or_none(session, paste_or_file: database.Paste | database.File | None) -> None:
    if paste_or_file is None:
        raise tornado.web.HTTPError(404, "Paste not found")
    
    if isinstance(paste_or_file, database.File):
        paste = paste_or_file.paste
    else:
        paste = paste_or_file

    if paste.exp_date < datetime.utcnow():
        session.delete(paste)
        session.commit()

        # TODO: consider removing this warning or making it an 
        # error that takes the reap interval into account.
        log.warning(
            "Paste was expired but still existed in the database."
        )
        raise tornado.web.HTTPError(404, "Paste not found")


def get_file(session: Session, slug: str) -> database.Paste:
    file = session.query(database.File).filter(database.File.slug == slug).one_or_none()
    error_if_expired_or_none(session, file)
    
    return file

def get_paste(session: Session, slug: str) -> database.Paste:
    paste = session.query(database.Paste).filter(database.Paste.slug == slug).one_or_none()
    error_if_expired_or_none(session, paste)
    
    return paste

def get_paste_by_removal(session: Session, slug: str) -> database.Paste:
    paste = session.query(database.Paste).filter(database.Paste.removal == slug).one_or_none()
    error_if_expired_or_none(session, paste)

    return paste