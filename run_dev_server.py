#! /usr/bin/env python

if __name__ == "__main__":
    from wiki import app
    app.run(debug=True, host="0.0.0.0", port=8000)
