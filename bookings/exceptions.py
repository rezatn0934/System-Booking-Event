from rest_framework.exceptions import APIException


class BusinessLogicException(APIException):
    status_code = 409
    default_detail = "Business rule violation."
    default_code = "business_logic"


class ResourceLockedException(APIException):
    status_code = 423
    default_detail = "The requested resource is locked."
    default_code = "resource_locked"


class ResourceExpiredException(APIException):
    status_code = 410
    default_detail = "The requested resource has expired."
    default_code = "resource_expired"
