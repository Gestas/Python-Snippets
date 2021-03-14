import logging
import keyring
import keyring.errors

logger = logging.getLogger(__name__)


def get_secret(secret_name, service_name):
    """ Return a secret or None if the secret does not exist."""
    try:
        return keyring.get_password(
            service_name=service_name, username=secret_name
        )
    except keyring.errors.KeyringError as err:
        logger.error(
            f"Error getting {service_name}: {secret_name} from the keyring."
        )
        logger.error(f"ERROR: {err}")


def set_secret(service_name, secret_name, secret) -> bool:
    try:
        keyring.set_password(
            service_name=service_name, username=secret_name, password=secret
        )
        return True
    except keyring.errors.PasswordSetError as err:
        logger.error(
            f"Error setting {service_name}: {secret_name} to the keyring."
        )
        logger.error(f"ERROR: {err}")
