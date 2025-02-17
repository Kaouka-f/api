def updatePassword(self, id, email, password, newPassword):
    query = {'email': email}
    try:
        result = self.collection.find(query)
        result_list = list(result)
        if result_list['password'] == password and result_list['email'] == email and result_list['confirm'] == False:
            update = {'$set': {'password': newPassword}}
            self.collection.update_one(query, update)
    except errors.PyMongoError as e:
        print(f"Error while working with MongoDB: {e}")
