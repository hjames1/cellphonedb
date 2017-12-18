from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import pandas as pd
from flask_restful import Resource

import json


class QueryBase(Resource):
    def __init__(self):
        self._msg = MIMEMultipart('form-data')
        self._errors = []
        self._attachments = []

    def _attach_error(self, error: json):
        self._errors.append(error)

    def _attach_csv(self, file_to_send, filename):
        attachment = MIMEBase('text', 'csv')
        attachment.set_payload(file_to_send)

        attachment.add_header("Content-Disposition", "attachment", filename=filename)

        self._attachments.append(attachment)

    def _attach_table(self, file_to_send, filename):
        attachment = MIMEBase('text', 'tab-separated-values')
        attachment.set_payload(file_to_send)

        attachment.add_header("Content-Disposition", "attachment", filename=filename)

        self._attachments.append(attachment)

    def _attach_json(self, data, at_first=False):
        attachment = MIMEBase('application', 'json')
        attachment.set_payload(json.dumps(data))

        if at_first:
            self._attachments = [attachment] + self._attachments

        else:
            self._attachments.append(attachment)

    def _attach_status(self, data={}):
        status = {"data": {}}

        if self._errors:
            status['errors'] = self._errors

        self._attach_json(status, at_first=True)

    def _commit_attachments(self):
        self._attach_status()

        for attach in self._attachments:
            self._msg.attach(attach)

    def _read_table(self, file, index_column_first=False):

        if file.content_type == 'text/csv':
            return pd.read_csv(file.stream, index_col=0 if index_column_first else None)

        if file.content_type == 'text/tab-separated-values':
            return pd.read_table(file.stream, index_col=0 if index_column_first else None)

        return None