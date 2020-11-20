from flask import Flask
from flask_restful import Api, Resource, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import os

server = 'group6project.database.windows.net'
database = 'cloudprojectdb'
username = os.environ.get('sql_username')
password = os.environ.get('sql_password')
driver= 'ODBC+Driver+17+for+SQL+Server'
connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
engine = SQLAlchemy.create_engine(SQLAlchemy, connection_string, {})

try:
    connection = engine.connect()
except Exception as ex:
    print('Database connection FAILED!:')
    print(ex)

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #No idea what this does, but it's set to false to suppress deprecation warning.
db = SQLAlchemy(app)

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'img_type': fields.String,
    'upload_date': fields.String,
    'path': fields.String
}

class Image(Resource):
    @marshal_with(resource_fields)
    def get(self, img_id):
        resultproxy = engine.execute(f"select * from Images where id = {img_id}")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                if (column == 'upload_date'):
                    value = temp[0] + ' ' + temp[1]
                else:
                    value = temp[0]
                d = {**d, **{column: value}}
            a.append(d)
        if not a:
            abort(404, message="404 cat not found")
        return a

class GetImageCount(Resource):
    def get(self):
        resultproxy = engine.execute(f"select COUNT(id) from Images where id != 0")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            # build up the dictionary
            d = {**d, **{"count": rowproxy[0]}}
            a.append(d)
        if not a:
            abort(404, message="404 cat not found")
        return a

class GetAllImages(Resource):
    @marshal_with(resource_fields)
    def get(self):
        resultproxy = engine.execute(f"SELECT * FROM Images where id != 0 ORDER BY id ASC")
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                temp = str(value).split()
                if (column == 'upload_date'):
                    value = temp[0] + ' ' + temp[1]
                else:
                    value = temp[0]
                d = {**d, **{column: value}}
            a.append(d)
        if not a:
            abort(404, message="404 cat not found")
        return a

api.add_resource(Image, "/images/<int:img_id>")
api.add_resource(GetImageCount, "/images/count")
api.add_resource(GetAllImages, "/images/")

if (__name__) == "__main__":
    app.run(debug=False)