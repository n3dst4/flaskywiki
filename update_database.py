#! /usr/bin/env python

if __name__ == "__main__":
    from wiki import engine, Base
    import wiki.models
    Base.metadata.create_all(engine)
