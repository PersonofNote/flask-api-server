# -*- encoding: utf-8 -*-

"""
Copyright (c) 2019 - present appSeed.us
"""

from api import application, db

@application.shell_context_processor
def make_shell_context():
    return {"application": application,
            "db": db
            }

if __name__ == '__main__':
    application.run(debug=False, host="0.0.0.0")
