def unPaying(self, id, email, password):
    # TODO: need authentication
    query = {'email': email}
    try:
        result = self.collection.find(query)
        result_list = list(result)
        if result_list['password'] == password and result_list['email'] == email and result_list['confirm'] == False:
            update = {'$unset': {'pay': True}}
            self.collection.update_one(query, update)
            return {'update': False}
        return {'update': True}
    except errors.PyMongoError as e:
        print(f"Error while working with MongoDB: {e}")
        self.log.log_crash("proxy Error in unPaying while working with MongoDB: " + str(e))
