class Admin:
    __admins = (1066757578, 704391766)
    @staticmethod
    def is_admin(user_id: int):
        return True if user_id in Admin.__admins else False

