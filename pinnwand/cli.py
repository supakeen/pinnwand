#!/usr/bin/env python
import sys

from datetime import datetime, timedelta

from pinnwand.models import Base, engine, session, Paste


def main():
    args = sys.argv[1:]

    if args:
        if args[0] == "init_db":
            Base.metadata.create_all(engine)

        if args[0] == "add":
            paste = Paste(
                "<html>hi</html>", lexer="html", expiry=timedelta(seconds=5)
            )

            session.add(paste)
            session.commit()

        if args[0] == "remove":
            paste = (
                session.query(Paste).filter(Paste.id == int(args[1])).first()
            )

            session.delete(paste)
            session.commit()

        if args[0] == "list":
            for paste in session.query(Paste).all():
                print(paste)

        if args[0] == "reap":
            pastes = (
                session.query(Paste)
                .filter(Paste.exp_date < datetime.now())
                .all()
            )

            for paste in pastes:
                session.delete(paste)
            session.commit()

            print(
                "[{}] Reaped {} expired pastes".format(
                    datetime.now().isoformat(), len(pastes)
                )
            )


if __name__ == "__main__":
    main()
