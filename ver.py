import random

_digits = 6


class VerificationCodeManager:
    _ver_dict = {}
    _ver_set = set()

    def generate(self, email_address):
        # if a ver code is existing, override it
        if email_address in self._ver_dict.keys():
            self._ver_set.remove(self._ver_dict[email_address])
            self._ver_dict.pop(email_address)
        while True:
            # ver_code = str([random.randint(0, 10) for _ in range(4)])
            ver_code = ''.join(chr(random.randint(48, 57)) for _ in range(_digits))
            # print(ver_code)
            if ver_code not in self._ver_set:
                break
        self._ver_dict[email_address] = ver_code
        self._ver_set.add(ver_code)
        return ver_code

    def verify(self, email_address, ver_code: str):
        temp = self._ver_dict.get(email_address)
        if temp is not None and temp == ver_code:
            self._ver_set.remove(self._ver_dict[email_address])
            self._ver_dict.pop(email_address)
            return True
        else:
            return False


_ver_code_manager = VerificationCodeManager()


def generate(email_address):
    return _ver_code_manager.generate(email_address)


def verify(email_address, ver_code):
    return _ver_code_manager.verify(email_address, ver_code)
