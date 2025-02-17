
import json
import socket
import server.proxy.src.pgIface as pgIface
from utils import send_confirmation_email

def create_confirmation_link(token):
    confirmation_link = f"http://localhost:8000/item?id={token}"
    return confirmation_link

def signUp(id, password, email):
    # document = {'id': id, 'email': email, 'password': password, 'confirm': True, 'pay': True}
    mongo_manager = pgIface.MongoDBManager('your_db_name', 'your_collection_name')
    try:
        query = {'email': email}
        exist = mongo_manager.find_documents(query)
        if len(exist) == 0:
            # Send id to confirmation
            data = {'req_type': 'confirmation' ,'id': id}
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("confirmation-service", 6000))
                s.sendall(data.encode())
            # Generate and send mail
            link = create_confirmation_link(id)
            send_confirmation_email(email, link)
            # Insert in db
            result = mongo_manager.insert_document({'id': id, 'email': email, 'password': password, 'confirm': True, 'pay': True})
            # logger.info("result = %s", result.acknowledged)
            if result.acknowledged:
                # logger.info("Document inserted successfully")
                return {'presubscribe': False}
            else:
                pass
                # logger.info("Insertion not acknowledged (error occurred)")
                # log.log_crash("proxy Insertion not acknowledged document: " + document)
        else:
            # logger.info("this email already have an account")
            pass
    except Exception as e:
        print("Error:", e)
        # log.log_crash("proxy error connect account : " + str(e))
    return {'presubscribe': True}

def signUpEntry():
    pass