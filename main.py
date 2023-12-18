from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api 
from models import Restoran as restoranModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session

session = Session(engine)

app = Flask(__name__)
api = Api(app)        

class BaseMethod():

    def __init__(self):
        self.raw_weight = {'nama_restoran': 3, 'harga': 4, 'rating_restoran': 3, 'pelayanan': 4, 'jarak': 5, 'estimasi_waktu_pengantaran': 5}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(restoranModel.no, restoranModel.nama_restoran, restoranModel.harga, restoranModel.rating_restoran, restoranModel.pelayanan,
                       restoranModel.jarak, restoranModel.estimasi_waktu_pengantaran)
        result = session.execute(query).fetchall()
        print(result)
        return [{'no': Restoran.no, 'nama_restoran': Restoran.nama_restoran, 'harga': Restoran.harga, 'rating_restoran': Restoran.rating_restoran,
                'pelayanan': Restoran.pelayanan, 'jarak': Restoran.jarak, 'estimasi_waktu_pengantaran': Restoran.estimasi_waktu_pengantaran} for Restoran in result]

    @property
    def normalized_data(self):
        harga_values = [data['harga'] for data in self.data]
        rating_restoran_values = [data['rating_restoran'] for data in self.data]
        pelayanan_values = [data['pelayanan'] for data in self.data]
        jarak_values = [data['jarak'] for data in self.data]
        estimasi_waktu_pengantaran_values = [data['estimasi_waktu_pengantaran'] for data in self.data]

        max_harga_value = max(harga_values) if harga_values else 1
        max_rating_restoran_value = max(rating_restoran_values) if rating_restoran_values else 1
        max_pelayanan_value = max(pelayanan_values) if pelayanan_values else 1
        max_jarak_value = max(jarak_values) if jarak_values else 1
        max_estimasi_waktu_pengantaran_value = max(estimasi_waktu_pengantaran_values) if estimasi_waktu_pengantaran_values else 1
        
        return[
            {
                'no': data['no'],
                'nama_restoran': data['nama_restoran'],
                'harga': data['harga'] / max_harga_value if max_harga_value != 0 else 0,
                'rating_restoran': data['rating_restoran'] / max_rating_restoran_value,
                'pelayanan': data['pelayanan'] / max_pelayanan_value,
                'jarak': data['jarak'] / max_jarak_value,
                'estimasi_waktu_pengantaran': data['estimasi_waktu_pengantaran'] / max_estimasi_waktu_pengantaran_value,
            }
            for data in self.data
            ]

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['harga'] ** self.weight['harga'] *
                    row['rating_restoran'] ** self.weight['rating_restoran'] *
                    row['pelayanan'] ** self.weight['pelayanan'] *
                    row['jarak'] ** self.weight['jarak'] *
                    row['estimasi_waktu_pengantaran'] ** self.weight['estimasi_waktu_pengantaran'],
                    'nama_restoran': row.get('nama_restoran', '')
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'ID': product['no'],
                'nama_restoran': product['nama_restoran'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data

class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'restoran': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value
    

class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'no': row['no'],
                'nama_restoran': row.get('nama_restoran'),
                'Score': round(row['harga'] * weight['harga'] +
                        row['rating_restoran'] * weight['rating_restoran'] +
                        row['pelayanan'] * weight['pelayanan'] +
                        row['jarak'] * weight['jarak'] +
                        row['estimasi_waktu_pengantaran'] * weight['estimasi_waktu_pengantaran'], 3)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'Restoran': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


class Restoran(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(restoranModel).order_by(restoranModel.no)
        result_set = query.all()
        data = [{'no': row.no, 'nama_restoran': row.nama_restoran, 'harga': row.harga, 'rating_restoran': row.rating_restoran, 'pelayanan': row.pelayanan, 
                'jarak': row.jarak, 'estimasi_waktu_pengantaran' : row.estimasi_waktu_pengantaran}
                for row in result_set]
        return self.get_paginated_result('restoran/', data, request.args), 200


api.add_resource(Restoran, '/restoran')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)
