'''
Created on Jun 19, 2013

@author: gluedig
'''

from fm_services import app
from flask import session, Response
from collections import Iterable
import Queue
import json

class GroupMemberUpdates(Iterable):
    def __init__(self, app, group_id):
        self.app = app
        self.group_id = group_id
        self.n = 0
        self.q = Queue.Queue()
        self.app.signals['group-member-add'].connect(self._grp_add_signal, self.app)
        self.app.signals['group-member-remove'].connect(self._grp_del_signal, self.app)
        
    def _grp_add_signal(self, sender, group_id, mac, **args):
        self.app.logger.debug(str.format("Added client: {0} to group: {1}", mac, group_id))
        self.q.put(('add-member', group_id, mac))
    
    def _grp_del_signal(self, sender, group_id, mac, **args):
        self.app.logger.debug(str.format("Removed client: {0} from group: {1}", mac, group_id))
        self.q.put(('remove-member', group_id, mac))
    
    def __iter__(self):
        while True:
            (op, group_id, mac) = self.q.get()
            if group_id == self.group_id:
                data = {'msgtype': op, 'group_id': group_id, 'client': mac}
                self.n += 1
                yield unicode("event: message\nid: {0}\ndata: {1}\n\n".format(self.n, json.dumps(data)))


@app.route('/updates/group', methods=["POST","GET"])
def group_updates():
    if 'group' not in session:
            return ("Client does not belong to any group\n", 404)
        
    group = session['group']
    return Response(GroupMemberUpdates(app, group), headers=[('cache-control','no-cache'), ('connection', 'keep-alive')],
        content_type='text/event-stream')


class FileboxUpdates(Iterable):
    def __init__(self, app, group_id):
        self.app = app
        self.group_id = group_id
        self.n = 0
        self.q = Queue.Queue()
        self.app.signals['file-upload'].connect(self._file_add_signal, self.app)

    def _file_add_signal(self, sender, mac, group_id, filename, **args):
        self.app.logger.debug(str.format("File uploaded client: {0} for group: {1} filename {2}",
                                     mac, group_id, filename))
        self.q.put(('file-upload', mac, group_id, filename))

    def __iter__(self):
        while True:
            (op, mac, group_id, filename) = self.q.get()
            if group_id == self.group_id:
                data = {'msgtype': op, 'group_id': group_id, 'client': mac, 'filename': filename}
                self.n += 1
                yield unicode("event: message\nid: {0}\ndata: {1}\n\n".format(self.n, json.dumps(data)))


@app.route('/updates/files', methods=["POST","GET"])
def files_updates():
    if 'group' not in session:
            return ("Client does not belong to any group\n", 404)

    group = session['group']
    return Response(FileboxUpdates(app, group), headers=[('cache-control','no-cache'), ('connection', 'keep-alive')],
        content_type='text/event-stream')
