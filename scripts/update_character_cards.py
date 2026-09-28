import struct
import zlib
import base64
import json
import os
import shutil

JS_PATH = os.path.join(os.path.dirname(__file__), 'eldoria_state_machine.js')
with open(JS_PATH, 'r', encoding='utf-8') as f:
    NEW_SCRIPT_CODE = f.read()

TARGET_PNGS = [
    '/home/nanhu2/comfyui/SillyTavern/data/default-user/characters/default_Seraphina_1.png',
    '/home/nanhu2/comfyui/SillyTavern/data/default-user/characters/Seraphina.png',
    '/home/nanhu2/comfyui/世界书/output/Eldoria.png',
]

def update_png(png_path):
    print(f'Processing {png_path}...')
    if not os.path.exists(png_path):
        print(f'  Skipped: {png_path} does not exist')
        return

    # Backup
    bak_path = png_path + '.bak_instant_cut'
    if not os.path.exists(bak_path):
        shutil.copy2(png_path, bak_path)
        print(f'  Created backup: {bak_path}')

    with open(png_path, 'rb') as f:
        sig = f.read(8)
        assert sig == b'\x89PNG\r\n\x1a\n', 'Invalid PNG signature'
        chunks = []
        while True:
            len_bytes = f.read(4)
            if not len_bytes:
                break
            length = struct.unpack('>I', len_bytes)[0]
            ctype = f.read(4)
            data = f.read(length)
            crc = f.read(4)
            chunks.append((ctype, data))
            if ctype == b'IEND':
                break

    new_chunks = []
    updated_count = 0
    for ctype, data in chunks:
        if ctype == b'tEXt':
            key, val = data.split(b'\x00', 1)
            if key in [b'chara', b'ccv3']:
                decoded_str = base64.b64decode(val).decode('utf-8')
                card_json = json.loads(decoded_str)
                th = card_json.get('data', {}).get('extensions', {}).get('tavern_helper', {})
                scripts = th.get('scripts', [])
                script_found = False
                for s in scripts:
                    if 'Eldoria' in s.get('name', ''):
                        s['content'] = NEW_SCRIPT_CODE
                        script_found = True
                if script_found:
                    updated_count += 1
                    print(f'  Updated script in {key.decode()} chunk')
                new_json_str = json.dumps(card_json, ensure_ascii=False)
                new_b64 = base64.b64encode(new_json_str.encode('utf-8'))
                new_data = key + b'\x00' + new_b64
                new_chunks.append((ctype, new_data))
                continue
        new_chunks.append((ctype, data))

    tmp_path = png_path + '.tmp'
    with open(tmp_path, 'wb') as f:
        f.write(sig)
        for ctype, data in new_chunks:
            f.write(struct.pack('>I', len(data)))
            f.write(ctype)
            f.write(data)
            crc = zlib.crc32(ctype + data) & 0xffffffff
            f.write(struct.pack('>I', crc))

    # Verify tmp file before moving
    with open(tmp_path, 'rb') as f:
        sig_test = f.read(8)
        assert sig_test == b'\x89PNG\r\n\x1a\n'
        while True:
            len_b = f.read(4)
            if not len_b: break
            l = struct.unpack('>I', len_b)[0]
            ct = f.read(4)
            dt = f.read(l)
            c = struct.unpack('>I', f.read(4))[0]
            assert c == (zlib.crc32(ct + dt) & 0xffffffff), f'CRC check failed for {ct}'
            if ct == b'tEXt':
                k, v = dt.split(b'\x00', 1)
                test_obj = json.loads(base64.b64decode(v).decode('utf-8'))
                assert 'data' in test_obj
            if ct == b'IEND': break

    shutil.move(tmp_path, png_path)
    print(f'Successfully updated {png_path} ({updated_count} chunks modified)')

if __name__ == '__main__':
    for path in TARGET_PNGS:
        update_png(path)
    print('All target PNGs updated successfully!')
