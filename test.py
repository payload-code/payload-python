
import os.path
from pathlib import Path
import requests

try:
    from . import payload as pl
except:
    import payload as pl



# file_path = os.path.join(os.getcwd(), 'logo_file.png')
# Path(file_path).touch()
# filename = 'logo_file_name.png'
# f = (open('logo_file.png', 'rb'))
# print('// ////////////////////////// Created File 1  // //////////////////////////')
# # print(f.keys())



# my_dict = {
#     'type':'one_time',
#     'description':'Payment Request',
#     'attachments[0][file]' : f,
#     'attachments[1][file]' : 123567787,
#     'amount':100.00, 
#     'processing_id':'3bz0zU99AX06SJwfMmfn0'
# }




# for k in my_dict:
#     if hasattr(my_dict[k], 'read'):
#         print(k, '//////////////FOUND THE FILE ATTR')
#     else:
#         print(k, my_dict[k],'//////////////Doesnt have file in it')



# data = {
#     id: 1324123.,
#     attachments : = [{file:f}]
# }






# file_path = os.path.join(os.getcwd(), 'logo_file.png')
# Path(file_path).touch()
# filename = 'logo_file_name.png'
# f = (open('logo_file.png', 'rb'))
# print('// ////////////////////////// Created File 1  // //////////////////////////')

# file_path2 = os.path.join(os.getcwd(), 'logo_file2.png')
# Path(file_path2).touch()
# filename2 = 'logo_file_name2.png'
# f2 = (open('logo_file2.png', 'rb'))
# print('// ////////////////////////// Created File 2 // //////////////////////////')

#prod key
pl.api_key = 'test_secret_key_3brS2TA5L42tNrngtrgUT'     

#local key
# pl.api_url = 'test_secret_key_3bzs0IlzojNTsM76hFOxT'
# pl.api_key = 'http://api.payload-dev.co:8000'


# print('//////////////////////////// Making the Request ////////////////////////////')
# payment_link = pl.PaymentLink.create(
#     type='one_time',
#     description='Payment Request',
#     attachments = [{'file':f}, {'file':f2}],
#     amount=100.00, 
#     processing_id='3bz0zU99AX06SJwfMmfn0'
# )
# print('//////////////////////////// Request Made ////////////////////////////')
# print(payment_link.attachments)


print('//////////////////////////// Making the Request ////////////////////////////')

payment = pl.Payment.create(
    amount=100.0,
    payment_method=pl.Card(
        card_number='4242 4242 4242 4242'
    )
)
print(payment)
print('//////////////////////////// Request Made ////////////////////////////')
