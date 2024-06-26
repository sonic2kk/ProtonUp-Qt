import os

from PySide6.QtDBus import QDBusConnection, QDBusMessage

from pupgui2.constants import DBUS_APPLICATION_URI, DBUS_DOWNLOAD_OBJECT_BASEPATH, DBUS_INTERFACES_AND_SIGNALS


def create_and_send_dbus_message(object: str, interface: str, signal_name: str, arguments: list, bus: QDBusConnection = QDBusConnection.sessionBus):

    """
    Create and send a QDBusMessage over a given bus.
    If no bus is given, will default to sessionBus
    """

    # i.e. /net/davidotek/pupgui2/Update
    object_path = os.path.join(DBUS_DOWNLOAD_OBJECT_BASEPATH, object)

    message: QDBusMessage = QDBusMessage.createSignal(object_path, interface, signal_name)
    message.setArguments(arguments)

    # Don't send the message if bus is not valid (i.e. DBus is not running)
    if bus.isConnected():
        bus.send(message)


def dbus_progress_message(progress: float, count: int = 0, bus: QDBusConnection = QDBusConnection.sessionBus()):

    """
    Create and send download progress (between 0 and 1) information with optional count parameter on a given bus.
    If no bus is given, will default to sessionBus.
    """

    arguments = {
        'progress': progress,
        'progress-visible': progress >= 0 and progress < 1,
        'count': count,
        'count-visible': count > 0
    }

    # We need to tell the 'Update' signal to update on DBUS_APPLICATION_URI,
    # plus an 'arguments' dict with some extra information
    #
    # i.e. { 'progress': 0.7, 'progress-visible': True }
    message_arguments = [
        DBUS_APPLICATION_URI,
        arguments
    ]

    launcher_entry_update = DBUS_INTERFACES_AND_SIGNALS['LauncherEntryUpdate']
    
    interface = launcher_entry_update['interface']
    signal = launcher_entry_update['signal']
    object = 'Update'

    create_and_send_dbus_message(object, interface, signal, message_arguments, bus=bus)


