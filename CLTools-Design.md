# CLTools Design Document
**Name**: Ashwin Chugh

##Classes and Data Structures

### Mailbox
* Holds all information pertinent to a specific mailbox

#### Fields
1. time: Datetime object responsible for holding the time of creation for
the mailbox
2. latest_message_date: Datetime object that retains the date of the newest
message recieved in the mailbox.
3. deprecated: A boolean value that if True means that the mailbox is old
and messages are no longer fetched from the server. Old messages are cached
and can always be read.
4. address: A string variable that holds the address of the email address.
5. __mailbox: Private pointer to the mailbox object from the onesecmail
wrapper.
6. messages: Dictionary of messages in a <message_id : message_object>
pair. Each message is an email.
7. ID: SHA1 representation of the mailbox. Used to distinguish each mailbox
from the other. Uses the time of creation as well as the email address to
generate the SHA1 string.

### Message
* Represents an email or message that is stored in the mailbox

#### Fields
1. mailbox: Pointer to an object of type Mailbox
2. ID: The message_id given by the onesecmail API. This is not generated
in this program. The ID is used to identify a specific message.
3. from_addy: The email address this email or message was sent from.
4. to_addy: The email address this email or message was directed towards.
5. date: Datetime object that holds the date and time when this mesasge was
sent.
6. subject: Subject line of the email or message.
7. body: The raw textual body of the email/message.
8. text_body: Any inputted text of the email.
9. html_body: HTML code embedded into the email/message.
10. attachments: A list of attachments. 

### Globals
* Runtime class that holds information of globally accessed data.

#### Fields
1. TIME_LIMIT: Class field that holds the time limit in minutes that
determines when a mailbox is old and should not be fetched from.
2. MAILBOXES: A list of Mailbox objects.
3. CURRENT_MAILBOX: Pointer to the currently active mailbox.
4. ATTACHMENTS_SAVE_PATH: Final string that holds the path to the directory
to save attachments to.
5. CLMAIL_PATH: Final string that holds path to the hidden .clmail directory.

### Utils
* Utility class that provides a wide array of helper methods including basic
IO operations, ensuring persistence, and runtime checks.

## Algorithms
### Mailbox
1. __init__(self, mailbox): Instantiates a Mailbox class from a onesecmail wrapper
mailbox.
2. download_attachments(self, message_id): Downloads all attachments embedded in a
specific message identified by message_id.
3. delete_attachments(self): Deletes all downloaded attachments from this mailbox.
4. fetch_messages(self, from_date=None): Fetches all messages from the server that
are newer than from_date.


### Message
1. __init__(self, ...): Initializes a Message object from all input attributes.

### Globals
1. prune_mailboxes(): Marks all mailboxes that are older than Globals.TIME_LIMIT
as deprecated. Ensures that future calls to fetch_messages no longer contact server
and only retrieve cached messages.

### Utils
1. read_file(filename: str, rel_path: str = ""): Only takes in files that have been
pickled and packed through the LZMA algorithm. Unpacks the file and then dumps the
serialized object.
2. write_file(filepath, date): Serializes the object represented by data through pickle.
Uses the LZMA algorithm to compress the file after the bytes have been written.
3. create_dir(dir_path: str): Creates a directory as defined by dir_path. dir_path must
be a path that holds the directory's name in it.
4. diff_time(time1: datetime, time2: datetime): Calculates the difference (in minutes)
between the two datetime objects. Assumes that time1 is of datetime that is newer than
time2.
5. initialize(): Ensures persistence. Loads up all active and cached email/mailboxes,
sets runtime data from last session. Returns True on a successful operation and False
otherwise.
6. save_state(): Ensures persistence. Saves all active and cached emails. Any changed
runtime data is saved so initialize() during the next session will begin operating with
the latest runtime data.
7. ensure_active_mailbox(): If the current mailbox is None, returns False and True
otherwise. Useful check to prevent common bugs and errors.



## Persistence
The most important attributes to save for persistence are the emails generated.
Initialize() in Utils.py ensures that all emails generated, unless manually deleted,
are loaded into runtime memory such that if the use must interact with the messages
or any aspect of any mailbox, all the data needed is available. 

Globals' attributes are also set in initialize from the latest session using a shared
serialized list for storage. Any changes or modifications are always noted and seen
through every instance of the program.

To reduce the risk of packet loss or accessing data which can no longer be accessed in
the servers, CLTools immediately downloads, serializes, and packs all messages recieved.
Consequently, any attachments sent in any emails are immediately downloaded once such
emails are fetched.

All downloaded content can be accessed at any time once saved. All downloaded content
can also be deleted manually or by deleting the mailbox. Once a mailbox is deleted, any
and all data associated with that mailbox are no longer recoverable.
