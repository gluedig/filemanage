'''
Created on Jun 18, 2013

@author: developer
'''
from fm_services import app
from werkzeug import secure_filename
from flask import send_from_directory, session, request
import os.path
from flask.templating import render_template

class FileBox(object):
    '''
    classdocs
    '''


    def __init__(self, app):
        '''
        Constructor
        '''
        self.app = app
        self.grp_mgr = app.services['group_manager']
        self.clt_mgr = app.services['client_manager']
        self.files = {}
    
    def _check_group(self, session):
        if 'mac' not in session:
            return ('No MAC in session', 404)
        mac = session['mac']
        if not self.clt_mgr.is_registered(mac):
            return (str.format('Client MAC: {0} not registered', mac), 404)
        
        if 'group' not in session:
            return ("Client does not belong to any group", 404)
        grp_id = session['group']
        
        if not self.grp_mgr.is_member(grp_id, mac):
            return (str.format("Client {0} does not belong to group {1}", mac, grp_id), 404)
        
        return None
    
    #web methods
    def list_files(self, session):
        ret = self._check_group(session)
        if ret:
            return ret
        
        grp_id = session['group']
        ret = ""
        if grp_id in self.files:
            ret += "\n".join(self.files[grp_id])
        
        return ret
    
    def upload(self, session, request):
        ret = self._check_group(session)
        if ret:
            return ret
        
        mac = session['mac']
        grp_id = session['group']
        if request.method == 'POST':
            req_file = request.files['file']
            if req_file:
                filename = secure_filename(req_file.filename)
                req_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                if grp_id not in self.files:
                    self.files[grp_id] = set()
                self.files[grp_id].add(filename)
                
                self.app.signals['file-upload'].send(self.app,
                                                     mac=mac, group_id=grp_id, filename=filename)

                return str.format("Client: {0} uploaded file: {1} for group: {2}",
                                  mac, filename, grp_id)
        return render_template('upload.html')
                
    def download(self, session, req_file):
        ret = self._check_group(session)
        if ret:
            return ret
        mac = session['mac']
        
        filename = secure_filename(req_file)
        found = None
        for file_grp_id in self.files:
            if filename in self.files[file_grp_id]:
                found = file_grp_id
                break
            
        if not found:
            return (str.format("File: {0} not found", filename), 404)
        
        if not self.grp_mgr.is_member(found, mac):
            return (str.format("Client {0} does not belong to group {1}", mac, found), 404)
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


app.services['filebox'] = FileBox(app)
this_service = app.services['filebox']
        
#===============================================================================
# filebox i/f
#===============================================================================
@app.route('/filebox/list')
def filebox_list_route():
    return this_service.list_files(session)

@app.route('/filebox/upload', methods=['GET', 'POST'])
def filebox_upload_route():
    return this_service.upload(session, request)

@app.route('/filebox/download/<req_file>')
def filebox_download_route(req_file):
    return this_service.download(session, req_file)        