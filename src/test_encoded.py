import utils

encodedId = utils.encodeId(1234, 5678)
print(encodedId)
id, privateId = utils.decodeId(encodedId)
print(id, privateId)