from flask import Flask, jsonify, request, send_file, make_response, abort, Response, current_app
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import controller as controller
import display as dsp
import unicodedata
import tempfile
import subprocess
import re
from shutil import which, rmtree, make_archive
from io import BytesIO

app = Flask(__name__, static_folder='static')
UPLOAD_FOLDER = './static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CORS(app, resources={r"/*":{'origins':"*"}})

@app.route('/api/get-screens', methods=['GET'])
def get_screens():
    try:
        return jsonify(controller.get_all_screens())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-screen/<int:screen_id>', methods=['GET'])
def get_screen(screen_id):
    try:
        return jsonify(controller.get_screen_by_id(screen_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
@app.route('/api/save-screen', methods=['POST'])
def save_screen():
    try:
        data = request.get_json()
        new_display = controller.save_screen(data)
        return jsonify(new_display)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/delete-screen/<int:screen_id>', methods=['DELETE'])
def delete_display(screen_id):
    try:
        controller.delete_screen(screen_id)
        return jsonify({'status': 'deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/update-screen/<int:screen_id>', methods=['PUT'])
def update_screen(screen_id):
    try:
        updated = controller.update_screen(screen_id, request.get_json())
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/get-displays', methods=['GET'])
def get_displays():
    try:
        return jsonify(controller.get_all_displays())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-display/<int:display_id>', methods=['GET'])
def get_display(display_id):
    try:
        return jsonify(controller.get_display_by_id(display_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/get-datasets', methods=['GET'])
def get_datasets():
    try:
        return jsonify(controller.get_all_data_sets())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-datasource', methods=['POST'])
def save_data_source():
    try:
        req_data = request.get_json()
        return jsonify(controller.save_datasource(req_data))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def custom_jsonify(data):
    response = make_response(jsonify(data))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/api/get-saved-datasources', methods=['GET'])
def get_saved_datasources():
    try:
        return custom_jsonify(controller.get_saved_datasources())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/get-saved-datasource/<int:uid>', methods=['GET'])
def get_saved_datasource(uid):
    try:
        return custom_jsonify(controller.get_saved_datasource(uid))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/delete-datasource/<int:uid>', methods=['DELETE'])
def delete_datasource(uid):
    try:
        controller.delete_datasource(uid)
        return jsonify({"status": "deleted", "uid": uid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh-datasource/<int:uid>', methods=['GET'])
def refresh_datasource(uid):
    try:
        updated = controller.force_refresh_datasource(uid)
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit-datasource', methods=['POST'])
def edit_datasource():
    payload = request.json
    uid = payload.get("uid")
    if not uid:
        return jsonify({"error": "Missing UID"}), 400

    controller.delete_datasource(uid)
    controller.save_datasource(payload)
    return jsonify({"success": True})

@app.route('/api/update-screen-widgets/<int:uid>', methods=['POST'])
def update_screen_widgets(uid):
    try:
        req_data = request.get_json()
        updated = controller.update_screen(uid, req_data)
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-screen-picture-bin/<int:s_id>/<int:d_id>', methods=['GET'])
def get_screen_picture(s_id, d_id):
    try:
        # Load display from controller
        screen = controller.get_screen_by_id(s_id)
        display = controller.get_display_by_id(d_id)
        output_h_path = f"./displays/bin_files/screen_{s_id}.bin"
        output_png_path = f"./displays/pictures/screen_{s_id}.png"

        if not screen:
            abort(404, description="Screen not found")

        # Render PNG from widgets
        dsp.render_display(screen, output_png_path, screen.get('isRotated', False))

        raw_png = open(output_png_path, 'rb').read()
        proc_png = dsp.transform_image(
            raw_png,
            screen.get('isRotated', False),
            screen.get('flipX', False),
            screen.get('flipY', False)
        )
        # overwrite
        with open(output_png_path, 'wb') as f:
            f.write(proc_png)

        # USER has to add functionality to convert the image to the correct format
        # Convert PNG to bin (raw data only)
        match display["type"]:
            case "1bpp":
                dsp.convert_image_to_1bpp_bin(output_png_path, output_h_path, display["resolutionX"], display["resolutionY"])
            case "4bpp":
                dsp.convert_image_to_4bpp_bin(output_png_path, output_h_path, display["resolutionX"], display["resolutionY"])
            case _:
                RuntimeError("Display type does not exist")
                abort(500, description="Failed to generate screen picture")


        bin_data = open(output_h_path, 'rb').read()
        return Response(
            bin_data,
            mimetype='application/octet-stream',
            headers={'Content-Length': str(len(bin_data))}
        )

    except Exception as e:
        print(f"Error in API: {e}")
        abort(500, description="Failed to generate screen picture")

@app.route('/api/get-sleep/<int:id>', methods=['GET'])
def get_sleep_time(id):
    return str(controller.get_sleep_display(id)), 200, {'Content-Type': 'text/plain'}


@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    print(filepath)
    file.save(dst=filepath)


    public_url = f'./static/uploads/{filename}'
    return jsonify({'url': public_url})

@app.route('/api/get-uploaded-image/<string:filename>', methods=['POST'])
def get_uploaded_image(filename):

    if filename == '':
        return jsonify({'error': 'No filename sent'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    print(filepath)
    e = send_file(filepath)
    print(e)
    return e

@app.route('/api/delete-uploaded-image/<string:filename>', methods=['DELETE'])
def delete_uploaded_image(filename):

    if filename == '':
        return jsonify({'error': 'No filename sent'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'ok': 'All good'}), 200
    else:
        return jsonify({'error': 'file does not exist'}), 400

def strip_diacritics(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

@app.route('/api/whisper', methods=['GET'])
def whisper():
    query = request.args.get('query', '').strip()
    path = request.args.get('path')

    if not query or not path or not os.path.exists(path):
        return jsonify(options=[])

    normalized_query = strip_diacritics(query)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            options = []
            for line in f:
                line_clean = line.strip()
                normalized_line = strip_diacritics(line_clean)
                if normalized_query in normalized_line:
                    options.append(line_clean)
                    if len(options) >= 10:
                        break
        return jsonify(options=options)
    except Exception as e:
        print(f"Error reading whisper file: {e}")
        return jsonify(options=[])

# Directory where your Arduino sketches live
SKETCHES_DIR = os.path.join(os.path.dirname(__file__), 'displays/codes')

# Path to Arduino CLI executable (env var override or just the command name)
CLI_PATH = 'arduino-cli.exe' if os.name == 'nt' else 'arduino-cli'

@app.route('/api/compile-sketch', methods=['POST'])
def compile_sketch():
    try:
        data = request.get_json() or {}
        sketch_name = data.get('sketch')
        display_info = data.get('display', {})
        display_id = str(display_info.get('id', ''))
        display_lib_version = display_info.get('esp32-lib-version', '')
        raw_name = display_info.get('name', '')
        params = display_info.get('compilation_flags', {})
        print(f"[COMPILING] params: {params}", flush=True)

        if not sketch_name:
            print("[COMPILING] No sketch specified", flush=True)
            return jsonify({'error': 'No sketch specified'}), 400
        if not raw_name or not display_id:
            print("[COMPILING] No display info provided", flush=True)
            return jsonify({'error': 'No display info'}), 400

        # sanitize into __VALID_C_MACRO__
        safe = re.sub(r'[^0-9A-Za-z_]', '_', raw_name)
        macro_name = f"__{safe}__"

        sketch_path = os.path.join(SKETCHES_DIR, sketch_name)
        if not os.path.isdir(sketch_path):
            print(f"[COMPILING] Sketch not found: {sketch_path}", flush=True)
            return jsonify({'error': 'Sketch not found'}), 404

        # patch Display.h
        dh = os.path.join(sketch_path, 'Display.h')
        if os.path.exists(dh):
            lines = []
            # Only match the *generated* macro, not the guard or other defines
            pat_display_macro = re.compile(r'^\s*#define\s+__.+?__\s*$')
            with open(dh, 'r', encoding='utf-8') as f:
                for L in f:
                    if L.startswith('#define DISPLAY_ID'):
                        # replace the ID line
                        lines.append(f'#define DISPLAY_ID "{display_id}"\n')
                    # replace only the *generated* display-name macro
                    elif pat_display_macro.match(L) and not L.startswith('#define __DISPLAY_H__'):
                        lines.append(f'#define {macro_name}\n')
                    else:
                        lines.append(L)
            with open(dh, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"[COMPILING] Patched Display.h -> ID={display_id}, NAME={macro_name}", flush=True)
        else:
            print(f"[COMPILING] Warning: Display.h not found at {dh}", flush=True)

        # Locate Arduino CLI
        cli_executable = CLI_PATH
        if not os.path.isabs(cli_executable):
            resolved = which(cli_executable)
            print(f"[COMPILING] which('{cli_executable}') -> {resolved}", flush=True)
            cli_executable = resolved

        print(f"[COMPILING] Using Arduino CLI at: {cli_executable}", flush=True)

        if not cli_executable or not os.path.exists(cli_executable):
            msg = (f"[COMPILING] '{CLI_PATH}' not found. "
                   "Install Arduino CLI and ensure it's on your PATH, or set ARDUINO_CLI_PATH.")
            print(msg, flush=True)
            return jsonify({'error': msg}), 500
        
        def parse_core_list(raw_output):
            lines = raw_output.strip().split('\n')
            if len(lines) < 2:
                return []

            headers = lines[0].split()
            parsed = []
            for line in lines[1:]:
                # Split based on columns (aligned spacing)
                parts = line.split(None, len(headers) - 1)
                if len(parts) == len(headers):
                    parsed.append(dict(zip(headers, parts)))
            return parsed

        if display_lib_version:
            # query installed cores
            proc = subprocess.run(
                [cli_executable, 'core', 'list'],
                check=True, stdout=subprocess.PIPE
            )
            raw = proc.stdout.decode('utf-8', errors='ignore')
            print(f"[COMPILING] Installed cores: {raw}", flush=True)

            parsed_cores = parse_core_list(raw)
            for core in parsed_cores:
                if core["ID"] == "esp32:esp32":
                    installed_version = core["Installed"]
                    print(f"[COMPILING] esp32:esp32 is currently at version {installed_version}")

            if installed_version != display_lib_version:
                print(f"[COMPILING] Installing esp32:esp32@{display_lib_version} (was {installed_version})", flush=True)
                subprocess.run([cli_executable, 'core', 'update-index'], check=True)
                subprocess.run(
                    [cli_executable, 'core', 'install', f'esp32:esp32@{display_lib_version}'],
                    check=True
                )
                print(f"[COMPILING] Installed esp32:esp32@{display_lib_version}", flush=True)
            else:
                print(f"[COMPILING] esp32:esp32 is already at the correct version", flush=True)
        # Prepare compile command
        output_dir = tempfile.mkdtemp()

        

        fqbn = display_info.get('fqbn', 'esp32:esp32:esp32')
        flags = display_info.get("compilation_flags", {})
        
        # add compilation flags to the fqbn if any
        if flags:
            opts = ",".join(f"{k}={v}" for k, v in flags.items())
            fqbn = f"{fqbn}:{opts}"

        cmd = [
            cli_executable, 'compile',
            '--fqbn', fqbn,
            sketch_path,
            '--output-dir', output_dir
        ]
        print(f"[COMPILING] Running compile command: {' '.join(cmd)}", flush=True)

        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except FileNotFoundError as e:
            msg = f"[COMPILING] Execution failed: {e}"
            print(msg, flush=True)
            return jsonify({'error': 'Arduino CLI not found or not executable', 'details': str(e)}), 500
        except subprocess.CalledProcessError as e:
            details = e.stderr.decode('utf-8', errors='replace')
            msg = f"[COMPILING] Compilation failed: {details}"
            print(msg, flush=True)
            return jsonify({'error': 'Compilation failed', 'details': details}), 500

        # Locate the compiled .bin file
        parts = {}
        try:
            for fname in os.listdir(output_dir):
                lower = fname.lower()
                if lower.endswith('.bin') and 'bootloader' in lower:
                    parts['boot'] = os.path.join(output_dir, fname)
                elif lower.endswith('.bin') and 'partition' in lower:
                    parts['part'] = os.path.join(output_dir, fname)
                elif lower.endswith('.ino.bin'):
                    parts['app']  = os.path.join(output_dir, fname)
        except FileNotFoundError as e:
            msg = f"[COMPILING] Error reading output dir: {e}"
            print(msg, flush=True)
            return jsonify({'error': 'Error reading output dir', 'details': str(e)}), 500

        # serve the merged file if it exists
        merged = next((f for f in os.listdir(output_dir) if f.endswith('merged.bin')), None)
        if merged:
            response = send_file(
                os.path.join(output_dir, merged),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name='merged.bin'
            )
            @response.call_on_close
            def _cleanup():
                rmtree(output_dir)
                print(f"[COMPILING] Cleaned up {output_dir}", flush=True)
            return response


        # we expect all three parts
        if not all(k in parts for k in ('boot','part','app')):
            #rmtree(output_dir)
            print(f"[COMPILING] Missing parts: {parts}", flush=True)
            return jsonify({'error': 'Could not find all binary parts'}), 500

        # merge them
        merged_path = os.path.join(output_dir, 'merged.bin')
        with open(merged_path, 'wb') as out:
            for path, addr in (
                (parts['boot'], 0x0000),
                (parts['part'], 0x8000),
                (parts['app'], 0x10000),
            ):
                # pad if we’re not at the right offset yet
                cur = out.tell()
                if cur < addr:
                    out.write(b'\xff' * (addr - cur))
                with open(path, 'rb') as src:
                    out.write(src.read())

        # serve the stitched image
        response = send_file(
            merged_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name='merged.bin'
        )

        @response.call_on_close
        def _cleanup():
            rmtree(output_dir)
            print(f"[COMPILING] Cleaned up {output_dir}", flush=True)

        return response

    except Exception as e:
        msg = f"[COMPILING] Unexpected error: {e}"
        print(msg, flush=True)
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

@app.route('/api/download-universal', methods=['GET'])
def download_universal():
    sketch_folder = os.path.join(SKETCHES_DIR, 'Supported_Displays')
    if not os.path.isdir(sketch_folder):
        return {'error': 'Universal code not found'}, 404

    # make a temp dir & zip it
    tmpdir = tempfile.mkdtemp()
    zip_base = os.path.join(tmpdir, 'universal')
    zip_path = make_archive(zip_base, 'zip', sketch_folder)

    def generate():
        with open(zip_path, 'rb') as f:
            chunk = f.read(8192)
            while chunk:
                yield chunk
                chunk = f.read(8192)
        # delete the temp dir after streaming
        try:
            rmtree(tmpdir)
            app.logger.debug(f"Removed temp dir {tmpdir}")
        except Exception as e:
            app.logger.error(f"Failed to remove {tmpdir}: {e}")

    headers = {
        'Content-Disposition': 'attachment; filename=Supported_Displays.zip',
        'Content-Type': 'application/zip'
    }
    return Response(generate(), headers=headers)

@app.route("/api/fonts")
def list_fonts_json():
    fonts_dir = os.path.join(current_app.static_folder, "fonts")
    files = sorted(
        f for f in os.listdir(fonts_dir)
        if f.lower().endswith((".ttf", ".otf"))
    )
    font_items = []
    for f in files:
        base = os.path.splitext(f)[0]
        # Capture letters until first non-letter
        m = re.match(r"^([A-Za-z]+)", base)
        family = m.group(1) if m else base
        font_items.append({
            "filename": f,
            "family":   family
        })
    return jsonify(font_items)

@app.route('/api/render-screen-image/<int:screen_id>', methods=['GET'])
def render_screen_image(screen_id):

    screen_data = controller.get_screen_by_id(screen_id)

    # render into an in-memory buffer
    buf = BytesIO()
    dsp.render_display(screen_data, output_path=buf, rotated=screen_data.get('isRotated', False))
    buf.seek(0)

    # return as PNG
    return send_file(
        buf,
        mimetype='image/png',
        as_attachment=False,
        download_name=f'screen_{screen_id}.png'
    )

if __name__ == "__main__":
    controller.initialize_instances_from_file()
    controller.start_auto_refresh()
    app.run(host="0.0.0.0", port=5000, use_reloader=False) #
