import os
import pickle
from datetime import datetime
import hashlib
from onesecmail.validators import DateRangeValidator
import lzma


class Mailbox:
    """
    Represents one mailbox instance. Holds the address, time of creation, and all received messages.
    """
    def __init__(self, mailbox):
        self.time = datetime.now()
        self.latest_message_date = None
        self.deprecated = False
        self.address = mailbox.address
        self.__mailbox = mailbox
        self.messages = {}
        m = hashlib.sha1()
        m.update(str(self.time.timestamp()).encode('utf-8'))
        m.update(self.address.encode('utf-8'))
        self.ID = m.hexdigest()

    def download_attachments(self, message_id):
        if not os.path.isdir(os.path.join(Globals.ATTACHMENTS_SAVE_PATH, f"{self.address} {self.ID[:7]}")):
            os.mkdir(os.path.join(Globals.ATTACHMENTS_SAVE_PATH, f"{self.address} {self.ID[:7]}"))
        if message_id not in self.messages.keys():
            return
        message = self.__mailbox.get_message(message_id)
        for attachment in message.attachments:
            message.download_attachment(attachment.get("filename"), os.path.join(Globals.ATTACHMENTS_SAVE_PATH,
                                                                                 f"{self.address} {self.ID[:7]}",
                                                                                 attachment.get("filename")))

    def delete_attachments(self):
        os.rmdir(os.path.join(Globals.ATTACHMENTS_SAVE_PATH, f"{self.address} {self.ID[:7]}"))

    def fetch_messages(self, from_date=None):
        if Utils.diff_time(datetime.now(), self.time) > Globals.TIME_LIMIT:
            self.deprecated = True
        if self.deprecated:
            return self.messages
        msg_dict = self.messages
        date_validator = DateRangeValidator(min_date=from_date)
        for email_message in self.__mailbox.get_messages([date_validator]):
            if self.latest_message_date is None:
                self.latest_message_date = email_message.date
            msg_dict[email_message.id] = Message(self, email_message.id, email_message.from_address,
                                                 email_message.to_address, email_message.date, email_message.subject,
                                                 email_message.body, email_message.text_body, email_message.html_body,
                                                 email_message.attachments)
            self.download_attachments(email_message.id)
            if email_message.date > self.latest_message_date:
                self.latest_message_date = email_message.date
        return msg_dict


class Message:
    """
    Represents a message/email that is in a mailbox.
    """

    def __init__(self, mailbox: Mailbox, message_id: int, from_address: str, to_address: str, date: str,
                 subject: str = None, body: str = None, text_body: str = None, html_body: str = None,
                 attachments: list = None):
        self.mailbox = mailbox
        self.ID = message_id
        self.from_addy = from_address
        self.to_addy = to_address
        self.date = date
        self.subject = subject
        self.body = body
        self.text_body = text_body
        self.html_body = html_body
        self.mailbox.messages[self.ID] = self
        self.attachments = attachments


class Globals:
    """
    Maintains globally used data. Serialized.
    """
    TIME_LIMIT = 60
    MAILBOXES = []
    CURRENT_MAILBOX = None
    ATTACHMENTS_SAVE_PATH = os.path.join(os.getcwd(), "Downloads")
    CLMAIL_PATH = os.path.join(os.getcwd(), ".clmail")

    @staticmethod
    def prune_mailboxes():
        """
        Marks all mailboxes that are older than TIME_LIMIT as deprecated.
        :return: Nothing
        """
        for mailbox in Globals.MAILBOXES:
            if Utils.diff_time(datetime.now(), mailbox.time) > Globals.TIME_LIMIT:
                mailbox.deprecated = True


class Utils:
    @staticmethod
    def read_file(filename: str, rel_path: str = ""):
        """
        Uses PICKLE alongside LZMA de-compression to read a LZMA compressed file and unpickle an object back into
        memory. Handles all operations in bytes.
        :param filename: The name of the file.
        :param rel_path: The relative path from the current working directory of the program.
        :return: The object de-compressed and unpickled. Returns None in the event of an error.
        """
        file = os.path.join(os.getcwd(), rel_path, filename)
        if not os.path.isfile(file):
            print(f"File does not exist. Couldn't find {file}")
            return None
        try:
            with lzma.open(file, mode="rb") as f:
                return pickle.load(f)
        except Exception as E:
            print(f"An error occured reading a file: {E}")

    @staticmethod
    def write_file(filepath, data):
        """
        Creates and pickles data to the file. After writing the bytes to the file, the file is then compressed using
        LZMA compression.
        :param filepath: The path of the file to create or overwrite. Must include filename in path.
        :param data: The data to put into the file.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            with lzma.open(os.path.join(filepath), mode="wb") as f:
                f.write(pickle.dumps(data, protocol=pickle.DEFAULT_PROTOCOL))
        except Exception as E:
            print(f"Unknown error occured. {E}")

    @staticmethod
    def create_dir(dir_path: str):
        """
        Creates a specified directory if the directory does not exist.
        :param dir_path: The path of the directory to create. Must include directory name.
        """
        if os.path.isdir(dir_path):
            return
        os.mkdir(dir_path)

    @staticmethod
    def diff_time(time1: datetime, time2: datetime):
        """
        Utility method used to calculate difference in time (minutes).
        :param time1: The newer timestamp.
        :param time2: The older timestamp.
        :return: The difference between the two timestamps in minutes.
        """
        return int((time1 - time2).total_seconds() // 60)

    @staticmethod
    def initialize():
        """
        Initializes persistence by reading data from last state.
        :return: True if successful, false otherwise
        """
        if not os.path.exists(Globals.CLMAIL_PATH):
            Utils.create_dir(Globals.CLMAIL_PATH)
            Utils.create_dir(Globals.ATTACHMENTS_SAVE_PATH)
        if not os.path.isdir(Globals.CLMAIL_PATH):
            print("We detected a corrupt file state. Any temporary mail data before has been removed and lost.")
            os.remove(Globals.CLMAIL_PATH)
            print("Please run the program again.")
            return False
        if os.path.isfile(os.path.join(Globals.CLMAIL_PATH, "Global")):
            global_data = Utils.read_file(os.path.join(Globals.CLMAIL_PATH, "Global"))
            Globals.TIME_LIMIT = global_data[0]
            Globals.MAILBOXES = global_data[1]
            Globals.CURRENT_MAILBOX = global_data[2]
            Globals.ATTACHMENTS_SAVE_PATH = global_data[3]
        return True

    @staticmethod
    def save_state():
        """
        Saves any changes and the current state of clmail in the respective files.
        :return: True if successful, false otherwise
        """
        if not os.path.exists(Globals.CLMAIL_PATH):
            Utils.create_dir(Globals.CLMAIL_PATH)
            Utils.create_dir(Globals.ATTACHMENTS_SAVE_PATH)
        if not os.path.isdir(Globals.CLMAIL_PATH):
            print("We detected a corrupt file state. Any temporary mail data before has been removed and lost.")
            os.remove(Globals.CLMAIL_PATH)
            print("Please run the program again.")
            return False
        Utils.write_file(os.path.join(Globals.CLMAIL_PATH, "Global"), [Globals.TIME_LIMIT, Globals.MAILBOXES,
                                                                       Globals.CURRENT_MAILBOX,
                                                                       Globals.ATTACHMENTS_SAVE_PATH])

    @staticmethod
    def ensure_active_mailbox():
        """
        Ensures the current mailbox is not None and is active.
        :return: True if active, False otherwise
        """
        if Globals.CURRENT_MAILBOX is None:
            return False
        return True
