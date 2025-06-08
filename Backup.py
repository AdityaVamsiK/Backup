# This program is intended to take automatic backup of the system to a known directory
import os
import shutil
import hashlib
import tempfile

# Displays Directory Structure in a directory tree format
def print_directory_tree(start_path, indent=''):
    for item in os.listdir(start_path):
        full_path = os.path.join(start_path, item)
        if os.path.isdir(full_path):
            print(f"{indent}{item}/")
            print_directory_tree(full_path, indent + '    ')
        else:
            print(f"{indent}{item}")

# Creates an exact replica of the directory structure without checking for its presence
def create_replica(src, dst):
    # Create a temporary directory for atomic operation
    dst_parent = os.path.dirname(dst)
    temp_dst = tempfile.mkdtemp(dir=dst_parent)

    try:
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            dest_dir = os.path.join(temp_dst, rel_path)
            os.makedirs(dest_dir, exist_ok=True)

            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_dir, file)
                shutil.copy2(src_file, dst_file)

        # Atomically replace old backup with the new one
        if os.path.exists(dst):
            shutil.rmtree(dst)
        os.replace(temp_dst, dst)
        print(f'---Replica Creation Success (Atomic)!---')

    except Exception as e:
        shutil.rmtree(temp_dst, ignore_errors=True)
        print(f'Error during atomic replica creation: {e}')
    print(f'---Replica Creation Successful!---')


def file_hash(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_all_files_and_dirs(root):
    all_files = set()
    all_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        all_dirs.add(rel_dir)
        for file in filenames:
            rel_file = os.path.join(rel_dir, file)
            all_files.add(rel_file)

    return all_files, all_dirs

# Displays the list of updated file, new files and removed files
def directory_diff(source, backup):
    src_files, src_dirs = get_all_files_and_dirs(source)
    bkp_files, bkp_dirs = get_all_files_and_dirs(backup)

    created_files = src_files - bkp_files
    deleted_files = bkp_files - src_files
    common_files = src_files & bkp_files

    updated_files = []
    for rel_path in common_files:
        src_path = os.path.join(source, rel_path)
        bkp_path = os.path.join(backup, rel_path)

        if file_hash(src_path) != file_hash(bkp_path):
            updated_files.append(rel_path)

    created_dirs = src_dirs - bkp_dirs
    deleted_dirs = bkp_dirs - src_dirs
    directory_diff_dict = {
        "created_files": sorted(created_files),
        "deleted_files": sorted(deleted_files),
        "updated_files": sorted(updated_files),
        "created_dirs": sorted(created_dirs),
        "deleted_dirs": sorted(deleted_dirs)
    }
    if directory_diff_dict['created_files']:
        print(f'Created files: ')
        for file in directory_diff_dict['created_files']:
            print(f'\t---{file}')

    if directory_diff_dict['deleted_files']:
        print(f'Deleted_files: ')
        for file in directory_diff_dict['deleted_files']:
            print(f'\t---{file}')

    if directory_diff_dict['updated_files']:
        print(f'Updated Files: ')
        for file in directory_diff_dict['updated_files']:
            print(f'\t---{file}')

    if directory_diff_dict['created_dirs']:
        print(f'Created Directories: ')
        for file in directory_diff_dict['created_dirs']:
            print(f'\t---{file}')

    if directory_diff_dict['deleted_dirs']:
        print(f'Deleted Directories: ')
        for file in directory_diff_dict['deleted_dirs']:
            print(f'\t---{file}')

    return directory_diff_dict


# Updates all the changed files, adds new files and directories, removes deleted files and directories
def update_backup(source, backup):
    # Work in a temp directory and then atomically replace the original
    backup_parent = os.path.dirname(backup)
    temp_backup = tempfile.mkdtemp(dir=backup_parent)

    try:
        # First copy everything from existing backup (if it exists)
        if os.path.exists(backup):
            create_replica(backup, temp_backup)

        # Apply updates to the temp backup
        diff = directory_diff(source, backup)

        for rel_dir in diff["created_dirs"]:
            os.makedirs(os.path.join(temp_backup, rel_dir), exist_ok=True)

        for rel_file in diff["created_files"] + diff["updated_files"]:
            src_file = os.path.join(source, rel_file)
            dst_file = os.path.join(temp_backup, rel_file)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)

        for rel_file in diff["deleted_files"]:
            try:
                os.remove(os.path.join(temp_backup, rel_file))
            except FileNotFoundError:
                pass

        for rel_dir in sorted(diff["deleted_dirs"], reverse=True):
            bkp_dir = os.path.join(temp_backup, rel_dir)
            if os.path.isdir(bkp_dir) and not os.listdir(bkp_dir):
                os.rmdir(bkp_dir)

        # Replace the old backup atomically
        if os.path.exists(backup):
            shutil.rmtree(backup)
        os.replace(temp_backup, backup)
        print(f'---File backup success (Atomic)!---')

    except Exception as e:
        shutil.rmtree(temp_backup, ignore_errors=True)
        print(f"Error during atomic update: {e}")
    print(f'---Backup Successful!---')
