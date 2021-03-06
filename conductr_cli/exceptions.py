import os

# FileNotFoundError is only available on > python 3.3
NOT_FOUND_ERROR = getattr(__builtins__, 'FileNotFoundError', OSError)


class MalformedBundleError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BundleResolutionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MalformedBundleUriError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BintrayResolutionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BintrayUnreachableError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BintrayCredentialsNotFoundError(Exception):
    def __init__(self, credential_file_path):
        self.credential_file_path = credential_file_path

    def __str__(self):
        return repr(self.value)


class MalformedBintrayCredentialsError(Exception):
    def __init__(self, credential_file_path):
        self.credential_file_path = credential_file_path

    def __str__(self):
        return repr(self.value)


class InsecureFilePermissions(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class WaitTimeoutError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ContinuousDeliveryError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InstanceCountError(Exception):
    def __init__(self, conductr_version, nr_of_containers, message):
        self.conductr_version = conductr_version
        self.nr_of_containers = nr_of_containers
        self.message = message

    def __str(self):
        return repr(self.message)


class BindAddressNotFound(Exception):
    def __init__(self, message):
        self.message = message

    def __str(self):
        return repr(self.message)


class SandboxImageNotFoundError(Exception):
    def __init__(self, component_type, image_version):
        self.component_type = component_type
        self.image_version = image_version

    def __str(self):
        return repr('{} {}'.format(self.component_type, self.image_version))


class SandboxImageNotAvailableOfflineError(Exception):
    def __init__(self, image_version):
        self.image_version = image_version

    def __str(self):
        return repr(self.image_version)


class JavaCallError(Exception):
    def __init__(self, message):
        self.message = message

    def __str(self):
        return repr(self.message)


class JavaVersionParseError(Exception):
    def __init__(self, java_version_output):
        self.java_version_output = java_version_output

    def __str(self):
        return repr(self.java_version_output)


class JavaUnsupportedVendorError(Exception):
    def __init__(self, vendor):
        self.vendor = vendor

    def __str(self):
        return repr(self.vendor)


class JavaUnsupportedVersionError(Exception):
    def __init__(self, jvm_version):
        self.jvm_version = jvm_version

    def __str(self):
        return repr(self.jvm_version)


class DockerValidationError(Exception):
    def __init__(self, messages):
        self.messages = messages

    def __str(self):
        return repr(os.linesep.join(self.messages))


class SandboxUnsupportedOsError(Exception):
    def __init__(self):
        pass

    def __str(self):
        return repr(self)


class SandboxUnsupportedOsArchError(Exception):
    def __init__(self):
        pass

    def __str(self):
        return repr(self)
