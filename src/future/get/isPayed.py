def isPayed(self, id):
    query = {'id': id}
    try:
        result = self.collection.find(query)
        result_list = list(result)
        return {'payed': result_list['pay']}
    except errors.PyMongoError as e:
        print(f"kaouka internal error: : {e}")