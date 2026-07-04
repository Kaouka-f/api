import socket
from helper.email import send_confirmation_email
# import server.proxy.src.pgIface as pgIface

def create_forgot_link(token):
    confirmation_link = f"http://localhost:8000/pass?id={token}"
    return confirmation_link

def forgotPassword(id, email):
    try:
        # query = {'email': email}
        # mongo_manager = pgIface.MongoDBManager('your_db_name', 'your_collection_name')
        # exist = mongo_manager.find_documents(query)
        # if exist:
        #     # Send id to confirmation
        #     data = {'req_type': 'forgot' ,'id': id}
        #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #         s.connect(("confirmation-service", 6000))
        #         s.sendall(data.encode())
        #     # Generate and send mail
        #     link = create_forgot_link(id)
        #     send_confirmation_email(email, link)
        #     return {'send': False}
        # else:
            pass
            # logger.info("this email already have an account")
    except Exception as e:
        print("Error:", e)
        # log.log_crash("proxy forgotpassword error : " + str(e))
    return {'send': True}
