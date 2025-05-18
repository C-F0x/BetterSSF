import os
import shutil
import zipfile
import time
import re

def process_ssf_files():

    os.makedirs('./TEMP', exist_ok=True)
    os.makedirs('./Converted', exist_ok=True)

    for filename in os.listdir('./To-Be-Convert'):
        if filename.endswith('.ssf'):
            src = os.path.join('./To-Be-Convert', filename)
            dst = os.path.join('./TEMP', filename)
            shutil.copy(src, dst)

    for ssf_file in os.listdir('./TEMP'):
        if not ssf_file.endswith('.ssf'):
            continue

        file_path = os.path.join('./TEMP', ssf_file)
        temp_extract = os.path.join('./TEMP', 'temp_extract')
        ini_path = os.path.join(temp_extract, 'phoneTheme.ini')

        try:

            with zipfile.ZipFile(file_path, 'r') as zf:
                zf.extractall(temp_extract)

            if os.path.exists(ini_path):

                with open(ini_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                content = re.sub(r'operational_skin=\d+', 'operational_skin=320', content)
                skin_match = re.search(r'skin_name=(.+)', content)
                skin_name = skin_match.group(1).strip() if skin_match else None

                if not skin_name:
                    print(f"跳过 {ssf_file}：未找到skin_name")
                    continue

                with open(ini_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                new_zip_path = os.path.join('./TEMP', 'temp.zip')
                with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, _, files in os.walk(temp_extract):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_extract)
                            zf.write(file_path, arcname)

                os.remove(file_path)
                os.rename(new_zip_path, file_path)


                timestamp = time.strftime("%Y%m%d%H%M%S")
                new_name = f"{skin_name}.ssf"
                dest_path = os.path.join('./Converted', new_name)

                if os.path.exists(dest_path):
                    new_name = f"{skin_name}.{timestamp}.ssf"
                    dest_path = os.path.join('./Converted', new_name)

                shutil.move(file_path, dest_path)

        except Exception as e:
            print(f"处理 {ssf_file} 时出错：{str(e)}")
        finally:

            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract)
    shutil.rmtree('./TEMP')

if __name__ == '__main__':
    process_ssf_files()