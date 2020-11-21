from flask import Flask
from flask_restful import Api, Resource, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os, uuid, datetime

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

class UploadImage(Resource):
    connection_string_blob = 'DefaultEndpointsProtocol=https;AccountName=cs71003bffda805345c;AccountKey=KdCm90f50B+/59bmb7F8A97ATIxbfMhHlz41BN4jpTR9bQKT5Bjp9yfPeZKYXDG613JQPoQHoe1lesbFjoADCA==;EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connection_string_blob)
    container_name = "blobcontainer" + str(uuid.uuid4())
    container_client = blob_service_client.create_container(container_name, public_access='blob')
    
    @marshal_with(resource_fields)
    def post(self, path):
        upload_file_path = path
        temp = upload_file_path.split('/')
        img_name = temp[len(temp) - 1]
        img_type = img_name.split('.')[1]
        img_path = 'https://cs71003bffda805345c.blob.core.windows.net/' + self.container_name + '/' + img_name

        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=img_name)
        print("\nUploading..." + img_name)

        try:
            # Upload the created file
            with open(upload_file_path, "rb") as data:
                blob_client.upload_blob(data)
            
            # Add entry to database
            response = engine.execute('SELECT MAX(id) FROM Images')
            img_id = int(response[0]['id']) + 1
            engine.execute(f"INSERT INTO Images (id, name, img_type, upload_date, path) VALUES ('{img_id}', '{img_name}', '{img_type}', '{str(datetime.datetime.now())[0: 22]}', '{img_path}')")
            print('Done...Images uploaded successfully.')
        except Exception as ex:
            print('Exception:')
            print(ex)

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

class GetImageByName(Resource):
    @marshal_with(resource_fields)
    def get(self, img_name):
        resultproxy = engine.execute(f"select * from Images where name = '{img_name}'")
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
api.add_resource(GetImageByName, "/images/<string:img_name>")
api.add_resource(GetImageCount, "/images/count")
api.add_resource(GetAllImages, "/images/")
api.add_resource(UploadImage, "/images/upload/<string:path>")

if (__name__) == "__main__":
    app.run(debug=False)