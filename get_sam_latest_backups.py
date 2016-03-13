import argparse
import os
import shutil
import tempfile
import time
import zipfile


def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(
            description='Process args for retrieving NE backups')
    parser.add_argument('-p', '--path', required=False, default='/opt/5620sam/nebackup/SROS', action='store',
                        help='Path to the directory with NE backups (by default /opt/5620sam/nebackup/SROS')
    parser.add_argument('-d', '--directory', default='~', action='store',
                        help='Directory to put extracted backups to')
    parser.add_argument('-z', '--zip', required=False, action='store_true',
                        help='perform archiving of extracted backups')
    args = parser.parse_args()
    return args


def zipdir(path, ziph):
    # https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    # ziph is zipfile handle

    # chdir to be able to archive relative paths in ziph.write function
    os.chdir(os.path.join(path, ".."))
    for root, dirs, files in os.walk(path):
        for my_file in files:
            ziph.write(os.path.relpath(os.path.join(root, my_file), os.path.join(path, '..')))


def main():
    """
    Command-line program for retrieving NE backups from SAM server.
    see http://noshut.ru/
    for detailed explanation
    """

    args = get_args()
    timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
    
    # compose dir name for storing latest backups and try to make that directory
    new_backups_dir = os.path.join(os.path.expanduser(args.directory), "NE_backups__" + timestamp)
    try:
        os.makedirs(new_backups_dir)
    except os.error:
        print "Couldn't create directory %s" % new_backups_dir

    # if specified path is a directory, traverse into it and copy latest backups
    if os.path.isdir(args.path):
        os.chdir(args.path)
        for NE_dir in os.listdir(args.path):
            # get real path of directory to be copied by means of symlink "latest"
            target_dir = os.path.realpath(os.path.join(os.path.abspath(NE_dir), 'latest'))
            # get date of latest backup and append it later to the new_backups_dir
            backup_date = os.path.split(target_dir)[-1]
            # copying directories
            shutil.copytree(target_dir, os.path.join(new_backups_dir, NE_dir, backup_date))
        print "Latest backups copied to the %s directory" % new_backups_dir
    else:
        print "Seems like path %s does not exist" % args.path

    # if archiving is needed
    if args.zip:
        print "Creating the archive..."
        tmp_dir = tempfile.mkdtemp()
        zipf = zipfile.ZipFile(os.path.join(tmp_dir, "NE_backups.zip"), 'w', zipfile.ZIP_DEFLATED)
        zipdir(new_backups_dir, zipf)
        zipf.close()
        shutil.move(os.path.join(tmp_dir, "NE_backups.zip"), new_backups_dir)
        shutil.rmtree(tmp_dir)
        print "Archive %s/NE_backups.zip created" % new_backups_dir

    return 0


# Start program
if __name__ == "__main__":
    main()
    # TODO: to add backup retrieval on a specified date
