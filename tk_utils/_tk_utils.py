""" TK utils

"""
from __future__ import annotations

import os

from tk_utils.api import (
        zipfile,
        shutil,
        pathlib,
        requests,
        dt,
        )

from tk_utils import config as cfg
from tk_utils._pprint import (
        colorize,
        )


class _Msg(list):
    """ Message to be printed
    """

    def add(self, 
            line: str,
            sep: bool = False,
            strip: bool = False,
            newline: bool = False,
            bold: bool = False,
            color: str|None = None,
            ):
        """  Adds a line line to the message

        Parameters
        ----------
        line : str
            The line to add
        sep : bool
            If True, insert separators
            Defaults to False
        strip : bool
            If True, strip the line first
            Defaults to False
        newline : bool
            If True, add a newline char after the (stripped) line
            Defaults to False
        bold : bool
            If True, line (and separators) will be printed in bold
            Defaults to False

        """
        new = [line if strip is False else line.strip()]
        if sep is True:
            _sep = '-' * max(len(line), 40)
            new = [_sep] + new + [_sep]
        if newline is True:
            new.append('')
        if color is not None:
            new = [colorize(x, color) for x in new]
        if bold is True:
            #   [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
            new = [f"\033[1m{x}\033[0m" for x in new]

        self.extend(new)

    def print(self, quiet: bool = False):
        """ Prints the current message (list of strings)
        """
        if quiet is False:
            print('\n'.join(self))

def _copy(src, dst) -> None:
    """ Copies all files from `src` to `dst`

    Parameters
    ----------
    src: path-like
        Location of the source folder

    dst: path-like
        Location of the destination folder
        Will be created if it does not exist

    """
    if src.name.startswith('.'):
        return
    elif src.is_dir() and src.name not in cfg.DIRS_TO_EXCL:
        children = sorted(src.iterdir())
        # Copy empty directory and filter non-empty ones
        if len(children) == 0:
            shutil.copytree(src, dst)
        else:
            [_copy(p, dst.joinpath(p.name)) for p in children]
    elif src.is_file():
        if not dst.parent.exists():
            dst.parent.mkdir(parents=True)
        shutil.copy2(src, dst)
    else:
        # This should only happen if file is a symbolic link
        return

def _print_msg(msg: str, 
               sep: bool = True,
               quiet: bool = False, 
               color: str = 'bold'):
    """ Prints a header message
    """
    _msg = _Msg()
    _msg.add(msg, sep=sep, color=color)
    _msg.print(quiet=quiet)

def backup(show_folder: bool = False, quiet: bool = False) -> None:
    """Backup files under the toolkit project folder

    This function will copy all (non-system) files under "toolkit" to a
    "dated" folder inside "toolkit/_backup". A new dated folder will be
    created every time this function is called.

    This function will exclude system files, hidden files (e.g., files
    starting with '.'),  the Dropbox folder, and the backup folder itself.

    Parameters
    ----------
    show_folder : bool
        If True, prints the location of the destination folder.
        Ignored if the "_backup" folder does not exist (will always be printed)
        Defaults to False

    quiet: bool, optional
        If True, do not display any messages.
        Defaults to False

    Usage
    -----
    >> import tk_utils
    >> tk_utils.backup()


    Example
    -------
    Suppose you only have the following files under toolkit:

     toolkit/               <- PyCharm project folder 
     |
     |__ toolkit_config.py
     |__ tk_utils/          <- this package
    
    After the backup, your toolkit folder will look like this:
    
     toolkit/               <- PyCharm project folder 
     |
     |__ _backup/                       <- Will be created 
     |  |__ <YYYY-MM-DD-HH:MM:SS>/          <- Represents the time of the backup
     |  |  |__ toolkit_config.py                <- backup
     |  |  |__ tk_utils/                        <- backup
     |
     |__ toolkit_config.py              <- original (not modified)
     |__ tk_utils/                      <- original (not modified)


    """
    # OLD:
    # now = dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    # NEW:
    now = dt.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    bkroot = cfg.PRJDIR.joinpath(cfg.BACKUP_DIR)

    if not bkroot.exists():
        show_folder = True


    msg = _Msg()
    msg.add("Backing up toolkit folder...", sep=True, bold=True)
    if show_folder is True or not bkroot.exists():
        msg.add(f'''Destination:
            
    toolkit/
    |__ {cfg.BACKUP_DIR}/
    |   |__ {now}/      <- New folder''', strip=True, newline=True)
    msg.print(quiet=quiet)


    bkdir = bkroot.joinpath(now)
    if not bkdir.exists():
        bkdir.mkdir(parents=True)

    for src in cfg.PRJDIR.iterdir():
        _copy(src, bkdir.joinpath(src.name))

    _print_msg('Done', sep=False, color=None, quiet=quiet)


class ZipFile(zipfile.ZipFile):
    """ Patched ZipFile class to prevent errors of the type

        ValueError: Empty filename.

        when calling extractall
    """

    def extractall(self, path=None, members=None, pwd=None):
        """Extract all members from the archive to the current working
           directory. `path' specifies a different directory to extract to.
           `members' is optional and must be a subset of the list returned
           by namelist().
        """
        if members is None:
            members = self.namelist()

        if path is None:
            path = os.getcwd()
        else:
            path = os.fspath(path)

        for zipinfo in members:
            if zipinfo == '/':
                continue
            self._extract_member(zipinfo, path, pwd)


def _unzip(tmp, dst):
    """  Wrapper around extractall

    """
    try:
        with zipfile.ZipFile(tmp) as zf:
            zf.extractall(dst)
    except:
        with ZipFile(tmp) as zf:
            zf.extractall(dst)




def sync_dbox(quiet: bool = False) -> None:
    """ Downloads the files from the Dropbox shared folder into "_dropbox".

    This function will download all files from the shared folder under
    DROPBOX_URL into the following folder:

    toolkit/
    |__ _dropbox/       <- Destination

    Files under "_dropbox" will be replaced.

    Parameters
    ----------
    quiet: bool, optional
        If True, do not display any messages.
        Defaults to False


    Usage
    -----
    To synchronize the Dropbox folder, open the PyCharm console and type:

        >> import tk_utils
        >> tk_utils.sync_dbox()

    This will download the current version of the Dropbox shared folder and
    place the files under 'toolkit/_dropbox'. All existing files inside
    _dropbox will be replaced:

     <DROPBOX>/
     |__ toolkit/            <- Dropbox shared folder (SOURCE)
     |   |__ data/           
     |   |__ lectures/       
     |   |    ...


     toolkit/               <- PyCharm project folder 
     |
     |__ _dropbox/           <- DESTINATION (only files under this folder will be updated)
     |   |__ data/               <- Same as <DROPBOX>/toolkit/data above
     |   |__ lectures/           <- Same as <DROPBOX>/toolkit/lectures above
     |   |   ...                 <- Same as <DROPBOX>/toolkit/... above
     | ...
     |__ data/               <- NOT a destination (will not be updated)
     |__ lectures/           <- NOT a destination (will not be updated)
     |   ...                 <- NOT a destination (will not be updated)
    
    If the _dropbox folder does not exist, it will be created.


    """
    # Call the backup
    backup(quiet=quiet)

    _print_msg("Downloading Dropbox files...", quiet=quiet)

    #msg = _Msg()
    #msg.add("Downloading Dropbox files...", sep=True, bold=True)
    #msg.print(quiet=quiet)

    tmp = cfg.PRJDIR.joinpath('toolkit_dropbox.zip')
    dst = cfg.PRJDIR.joinpath(cfg.DBOX_DIR)

    if not dst.exists():
        dst.mkdir(parents=True)

    r = requests.get(cfg.DROPBOX_URL)
    with open(tmp, 'wb') as fobj:
        fobj.write(r.content)

    _unzip(tmp, dst)

    tmp.unlink()
    _print_msg('Done', sep=False, color=None, quiet=quiet)



def update() -> None:
    """ Updates the tk_utils module with the current version in Dropbox
    """
    _print_msg("Updating the tk_utils module...", quiet=False)

    # First sync (and backup)
    sync_dbox(quiet=True)

    # then update
    dbox = cfg.PRJDIR.joinpath(cfg.DBOX_DIR)
    src = dbox.joinpath('tk_utils')
    dst = cfg.PRJDIR.joinpath('tk_utils')


    _copy(src=src, dst=dst)

    _print_msg('Done', sep=False, color=None, quiet=False)


















