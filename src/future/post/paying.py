def paying(self, id, offer, payId):
    # TODO: need authentication
    # ask pay backend to pay and send info
    query = {'id': id}
    try:
        result = self.collection.find(query)
        result_list = list(result)
        if result_list > 0:
            update = {'$set': {'pay': False, 'offer': offer, 'payId': payId}}
            self.collection.update_one(query, update)
        return 0
    except errors.PyMongoError as e:
        print(f"Error while working with MongoDB: {e}")
        self.log.log_crash("proxy Error in paying while working with MongoDB: " + str(e))
