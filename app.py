from flask import Flask
from flask_restful import Api, Resource, abort, fields, marshal_with, reqparse
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient
import os, datetime, sys, base64, urllib, uuid

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
    sys.exit()

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    container_name = 'blobcontainer8b009926-54c3-4286-858b-daabadfe43f3'

    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('img_base64_message')
        args = parser.parse_args()
        base64_message = args['img_base64_message']
        base64_img_bytes = base64_message.encode('utf-8')

        with open('decoded_image.png', 'wb') as file_to_save:
            decoded_image_data = base64.decodebytes(base64_img_bytes)
            file_to_save.write(decoded_image_data)
        img_name = str(uuid.uuid4())
        img_type = '.png'
        img_path = 'https://cs71003bffda805345c.blob.core.windows.net/' + self.container_name + '/' + img_name + img_type

        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=img_name+img_type)
        print(f"\nUploading {img_name}{img_type}...")

        try:
            # Upload the created file
            with open('decoded_image.png', "rb") as data:
                blob_client.upload_blob(data)
            print(f"{img_name}{img_type} uploaded to storage account as blob!")
        except Exception as ex:
            print('Blob upload failed!')
            print(ex)
            abort(400)
        
        try:
            # Add entry to database
            response = engine.execute('SELECT MAX(id) FROM Images')

            val = 0
            for rowproxy in response:
                # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
                for column, value in rowproxy.items():
                    val = value
            img_id = val + 1

            engine.execute(f"INSERT INTO Images (id, name, img_type, upload_date, path) VALUES ('{img_id}', '{img_name}', '{img_type}', '{str(datetime.datetime.now())[0: 22]}', '{img_path}')")
            print(f"**SUCCESS {img_name}{img_type} added to database successfully!")
        except Exception as ex:
            print('Database entry failed!')
            print(ex)
            blob_client.delete_blob(blob=img_name)
            abort(400)
        os.remove('decoded_image.png')

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
api.add_resource(UploadImage, "/images/upload/")

if (__name__) == "__main__":
    app.run(debug=False)
