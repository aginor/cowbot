# Copyright 2018 Andreas Löf <andreas@alternating.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import Flask, jsonify

app = Flask(__name__)

app.config['FLASK_DEBUG'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = False

class CowsayError(Exception):

    def __init__(self,message) -> None:
        super().__init__()
        self.message = message


def _validate_token(token):
    import os
    own_token = os.environ['SLACK_TOKEN']
    return token == own_token


def _get_cowsay(text = 'moo'):
    import requests
    headers = {'Accept': 'text/plain'}
    r = requests.get('http://cowsay.io/say/{}'.format(text), headers=headers)
    if r.status_code != 200:
        raise CowsayError("The cow won't moo at the moment")
    return r.text


@app.route('/say', methods=['POST'])
def cowsay():
    from flask import request
    import json

    if request.method != 'POST':
        return ""

    if 'token' not in request.form or not _validate_token(request.form['token']):
        return ""

    resp = {}
    cow = None
    try:
        cow = "```{}```".format(_get_cowsay(request.form['text']) if 'text' in request.form else _get_cowsay())
        resp['response_type'] = 'in_channel'
    except CowsayError as e:
        cow = e.message
    resp['text'] = cow
    resp['mrkdwn'] = True
    return jsonify(resp)




if __name__ == '__main__':
    app.run()
