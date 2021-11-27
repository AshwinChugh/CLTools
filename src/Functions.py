from onesecmail import OneSecMail
from Utils import Globals, Mailbox, Utils


def create(args):
    if len(args) != 0:
        print("Invalid Arguments.")
        return
    mailbox = Mailbox(OneSecMail.get_random_mailbox())
    Globals.MAILBOXES.append(mailbox)
    if Globals.CURRENT_MAILBOX is None:
        Globals.CURRENT_MAILBOX = mailbox
    print(f"Mailbox created: {mailbox.address}\nID: {mailbox.ID}")
    print("Type 'clmail ls' to list out all available mail addresses.")


def ls(args):
    if len(args) != 1:
        print("Invalid Arguments.")
        return
    Globals.prune_mailboxes()
    for mailbox in Globals.MAILBOXES:
        if not mailbox.deprecated and (args[0] == "-active" or args[0] == "-all"):
            print(f"<{mailbox.ID[:7]} | {mailbox.address}>")
        if mailbox.deprecated and (args[0] == "-cached" or args[0] == "-all"):
            print(f"<{mailbox.ID[:7]} | {mailbox.address}> [{'DEPRECATED' if mailbox.deprecated else ''}]")
    print(f"If no mailboxes were printed, then there are no mailboxes under the flag {args[0]}.")


def setcurr(args):
    if len(args) != 1:
        print("Invalid Arguments.")
        return
    tmp = next((x for x in Globals.MAILBOXES if x.ID[:len(args[0])] == args[0]), None)
    if tmp is not None:
        Globals.CURRENT_MAILBOX = tmp
        print(f"Current mailbox set to mailbox: {tmp.ID}")
        return
    print("Invalid mailbox ID entered.")


def ls_messages(args):
    if len(args) != 0:
        print("Invalid Arguments.")
        return
    if not Utils.ensure_active_mailbox():
        print("The current mailbox is not initialized. Failed to list messages.")
        return
    Globals.CURRENT_MAILBOX.messages = Globals.CURRENT_MAILBOX.fetch_messages(
        Globals.CURRENT_MAILBOX.latest_message_date)
    if len(Globals.CURRENT_MAILBOX.messages.keys()) == 0:
        print("Current mailbox is empty.")
        return
    for message_id in Globals.CURRENT_MAILBOX.messages.keys():
        message = Globals.CURRENT_MAILBOX.messages.get(message_id)
        print(f"< ID: {message_id}\nFrom: {message.from_addy}\nSubject: {message.subject}\nDate: {message.date}>\n")


def cat(args):
    verbose = False
    if len(args) != 1:
        if len(args) == 2:
            if args[1] == "-v":
                verbose = True
            else:
                print("Invalid Arguments.")
                return
        else:
            print("Invalid Arguments.")
            return
    if not Utils.ensure_active_mailbox():
        print("The current mailbox is not initialized. Failed to read message.")
        return
    if int(args[0]) not in Globals.CURRENT_MAILBOX.messages.keys():
        print("Incorrect message ID.")
        return
    message = Globals.CURRENT_MAILBOX.messages.get(int(args[0]))
    res = f"From: {message.from_addy}\nSubject: {message.subject}\nDate: {message.date.astimezone()}\n" \
          f"\n{message.text_body}\n" \
          f"Attachments\n{message.attachments}\n"
    if not verbose:
        print(res)
        return
    res += f"RAW BODY\n{message.body}\nHTML_BODY\n{message.html_body}\n"
    print(res)


def download_attachments(args):
    if len(args) != 1:
        print("Invalid Arguments.")
        return
    if not Utils.ensure_active_mailbox():
        print("The current mailbox is not initialized. Failed to read message.")
        return
    if int(args[0]) not in Globals.CURRENT_MAILBOX.messages.keys():
        print("Incorrect message ID.")
        return
    res = input(f"The current installation directory is {Globals.ATTACHMENTS_SAVE_PATH}.\n"
                f"Press Y to continue installing attachments here and anything else to cancel the operation.\n"
                f"To change installation directory, use the 'cd' command.\n")
    if res.lower() != 'y':
        print("Operation cancelled.")
        return
    Globals.CURRENT_MAILBOX.download_attachments(int(args[0]))


def remove_mailbox(args):
    if len(args) != 1:
        print("Invalid Arguments.")
        return
    tgt = next((x for x in Globals.MAILBOXES if x.ID[:len(args[0])] == args[0]), None)
    if tgt == Globals.CURRENT_MAILBOX:
        Globals.CURRENT_MAILBOX = None
    if tgt is None:
        print("No mailbox with that ID exists.")
        return
    id = tgt.ID
    tgt.delete_attachments()
    Globals.MAILBOXES.remove(tgt)
    print(f"Removed Mailbox {id}")