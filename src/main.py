import Utils
import sys
from Functions import create, cat, setcurr, ls, ls_messages, download_attachments, remove_mailbox


def main():
    if len(sys.argv) == 1:
        print("You must enter a command.")
        return 0
    if not Utils.Utils.initialize():
        print("Critical Error During Initialization Process")
        return -1
    if sys.argv[1] == "create":
        create(sys.argv[2:])
    elif sys.argv[1] == "ls":
        ls(sys.argv[2:])
    elif sys.argv[1] == "set-curr":
        setcurr(sys.argv[2:])
    elif sys.argv[1] == "ls-messages":
        ls_messages(sys.argv[2:])
    elif sys.argv[1] == "cat":
        cat(sys.argv[2:])
    elif sys.argv[1] == "pull":
        download_attachments(sys.argv[2:])
    elif sys.argv[1] == "rm":
        remove_mailbox(sys.argv[2:])
        pass
    elif sys.argv[1] == "curr":
        if Utils.Globals.CURRENT_MAILBOX is None:
            print("No mailbox has been created.")
        else:
            print(f"<{Utils.Globals.CURRENT_MAILBOX.ID[:7]} | {Utils.Globals.CURRENT_MAILBOX.address}>")
    else:
        print("Invalid Command.")
    Utils.Utils.save_state()


# command to change TIME_LIMIT


if __name__ == "__main__":
    sys.exit(main())
