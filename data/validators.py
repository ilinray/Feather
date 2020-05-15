# This file includes functions which check whether everything is correct


from flask import request, session, redirect, url_for
from .db_funcs import DialogConnector, MessageConnector, UserConnector

# class methonds, which wound be decorated via @decorate_classes
methods = set(('get', 'post', 'patch', 'delete'))


class HttpError(Exception):
    # Base HTTP error
    pass


def create_http_error(code, reason):
    # Creates Exeption with data
    class HttpError_with_data(HttpError):
        pass

    HttpError_with_data.code = code
    HttpError_with_data.reason = reason

    return HttpError_with_data


def decorate_classes(wrapper):
    # Makes decorators to also decorate classes
    def decorated_wrapper(obj):
        if isinstance(obj, type):
            for funcname in set(dir(obj)) & methods:
                setattr(obj, funcname, wrapper(getattr(obj, funcname)))
            return obj
        return wrapper(obj)
    return decorated_wrapper


def check(*funcs):
    # Checks if everything is correct
    @decorate_classes
    def wrapper(func):
        def wrapped_func(*args, **kwargs):
            for f in funcs:
                try:
                    new_kwargs = f(*args, **kwargs)
                except HttpError as error:
                    return {'status': 'ER',
                            'reason': error.reason}, error.code
                else:
                    for key, value in new_kwargs.items():
                        if key not in kwargs.keys():
                            kwargs[key] = value
            return func(*args, **kwargs)
        return wrapped_func
    return wrapper


def get_args(**needed):
    # parses URL kwargs for functions
    def wrapper(func):
        def wrapped_func(*args, **kwargs):
            for needed_arg, needed_type in needed.items():
                if needed_arg in kwargs.keys():
                    continue
                try:
                    arg = needed_type(request.args[needed_arg])
                except (TypeError, ValueError):
                    er = f'argument {needed_arg} has wrong type.'
                    er += ' needed - {needed_type.__name__}'
                    raise create_http_error(400, er)
                except KeyError:
                    msg = f'no argument {needed_arg} found'
                    raise create_http_error(400, msg)
                else:
                    kwargs[needed_arg] = arg
            return func(*args, **kwargs)
        return wrapped_func
    return wrapper


@get_args(uid=int)
def correct_uid(*args, **kwargs):
    # Checks if uid is equal to uid in session
    uid = kwargs['uid']
    if session['logged_in'] != uid:
        raise create_http_error(401, 'you are not logged in')
    return {'uid': uid}


@get_args(dialog_id=int)
def dialog_exists(*args, **kwargs):
    # Checks if dialog is existing
    if not DialogConnector.exists_from_id(kwargs['dialog_id']):
        raise create_http_error(404, f'dialog {kwargs["dialog_id"]} not found')
    return {'dialog_id': kwargs['dialog_id']}


@get_args(uid=int, dialog_id=int)
def dialog_belongs_to_user(*args, **kwargs):
    # Checks if dialog belongs to user
    dial = DialogConnector.from_id(kwargs['dialog_id'])
    if kwargs['uid'] not in dial.users_id:
        raise create_http_error(401, 'you are not in the chat')
    return {'dialog_id': kwargs['dialog_id'],
            'dial': dial}


@get_args(uid=int)
def user_exists(*args, **kwargs):
    # Checks existance
    if not UserConnector.exists_from_id(kwargs['uid']):
        raise create_http_error(404, f'user {kwargs["uid"]} not found')
    return {'uid': kwargs['uid']}


@get_args(message_id=int)
def message_exists(*args, **kwargs):
    # Another check-function
    if not MessageConnector.exists_from_id(kwargs['message_id']):
        raise create_http_error(
            404, f'message {kwargs["message_id"]} not found')
    return {'message_id': kwargs['message_id']}


@get_args(uid=int, message_id=int)
def message_belongs_to_user(*args, **kwargs):
    # Check function
    msg = MessageConnector.from_id(kwargs['message_id'])
    if msg.entry.user_id != kwargs['uid']:
        raise create_http_error(401, f'not your message')
    return {'message_id': kwargs['message_id'],
            'msg': msg}


@get_args(uid=int, dialog_id=int)
def dialog_hosted_by_user(*args, **kwargs):
    # Check function
    dial = DialogConnector.from_id(kwargs['dialog_id'])
    if kwargs['uid'] != dial.entry.host_id:
        raise create_http_error(401, 'you are not the host')
    return {'dialog_id': kwargs['dialog_id'],
            'dial': dial}
