from uuid import uuid4


_receivers = []  # a list of the receivers' email addresses


def create_receiver(email_address):

    global _receivers

    email_object = {"id": uuid4(), "email": email_address}
    _receivers.append(email_object)

    return email_object


def receiver_email_exists(email_address):

    global _receivers

    return email_address in {email_obj["email"] for email_obj in _receivers}


def get_receivers():

    global _receivers

    return _receivers


def get_receivers_emails():

    global _receivers

    return [email_object["email"] for email_object in _receivers]


def get_receiver(index):

    email_object = None

    for test_email in _receivers:
        if test_email["id"] == index:
            email_object = test_email
            break

    return email_object


def delete_receivers():

    global _receivers

    _receivers.clear()

    return _receivers


def delete_receiver(email_object):

    global _receivers

    _receivers.remove(email_object)

    return email_object
