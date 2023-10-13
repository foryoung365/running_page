import argparse
import os
import sqlite3
import garth
from garmin_sync import Garmin  # Assuming this is from your previous script

def connect_db(local_dir):
    db_path = os.path.join(local_dir, 'uploaded_files.db')
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute('CREATE TABLE IF NOT EXISTS uploaded_files (filename TEXT PRIMARY KEY)')
    return conn

def get_uploaded_files(conn):
    cursor = conn.execute('SELECT filename FROM uploaded_files')
    return {row[0] for row in cursor}

def mark_as_uploaded(conn, filename):
    with conn:
        conn.execute('INSERT INTO uploaded_files (filename) VALUES (?)', (filename,))

def main(args):
    garmin_email = args.Garmin_email
    garmin_password = args.Garmin_password
    local_dir = args.local_dir
    
    if not os.path.exists(local_dir):
        print(f"Directory not found: {local_dir}")
        return
    
    # Configure and login to Garmin
    garth.configure(domain="garmin.com")  # Use garmin.cn if you are in China
    garth.login(garmin_email, garmin_password)
    client = Garmin(garth.client.dumps(), auth_domain=None)  # Assuming this is from your previous script
    
    conn = connect_db(local_dir)
    uploaded_files = get_uploaded_files(conn)
    
    fit_files_found = False
    for filename in os.listdir(local_dir):
        if filename.endswith('.fit'):
            fit_files_found = True
            if filename not in uploaded_files:
                file_path = os.path.join(local_dir, filename)
                with open(file_path, 'rb') as file:
                    file_body = file.read()
                    files = {"file": (filename, file_body)}
                    try:
                        res = client.req.post(client.upload_url, files=files, headers=client.headers)  # Assuming req is your http client
                        if res.status_code == 200:
                            print(f'Successfully uploaded: {filename}')
                            mark_as_uploaded(conn, filename)
                        else:
                            print(f'Failed to upload: {filename}. Response code: {res.status_code}')
                    except Exception as e:
                        print(f'Error uploading {filename}: {str(e)}')

    if not fit_files_found:
        print(f"No .fit files found in directory: {local_dir}")

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("Garmin_email", help="Email of Garmin account")
    parser.add_argument("Garmin_password", help="Password of Garmin account")
    parser.add_argument("local_dir", help="Directory containing .fit files to upload")
    args = parser.parse_args()
    main(args)
