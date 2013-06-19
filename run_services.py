'''
Created on Jun 19, 2013

@author: developer
'''

from services import app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')