# -*- encoding: utf-8 -*-

"""
Copyright (c) 2019 - present applicationSeed.us
"""

from api import application, db

@application.shell_context_processor
def make_shell_context():
    return {"application": application,
            "db": db
            }

if __name__ == '__main__':
    application.run(debug=True, host="0.0.0.0")
