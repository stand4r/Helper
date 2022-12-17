import pyrogram

number = "+79171418765"
api_id = 7640328
api_hash = "e8fecf361251bc064b959f193f04a308"
session = pyrogram.Client("23323", api_id, api_hash)
session.start()
print(session.get_me())