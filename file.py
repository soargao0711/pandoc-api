from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        
        if not data or 'input' not in data:
            return jsonify({"error": "Missing 'input' field"}), 400
        
        input_content = data.get('input')
        from_format = data.get('from', 'markdown')
        to_format = data.get('to', 'html')
        
        result = subprocess.run(
            ['pandoc', f'--from={from_format}', f'--to={to_format}'],
            input=input_content,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({
                "error": "Pandoc conversion failed",
                "details": result.stderr
            }), 400
        
        return jsonify({
            "success": True,
            "output": result.stdout
        }), 200
    
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Conversion timeout"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/convert/file', methods=['POST'])
def convert_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        from_format = request.form.get('from', 'markdown')
        to_format = request.form.get('to', 'html')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        content = file.read().decode('utf-8')
        
        result = subprocess.run(
            ['pandoc', f'--from={from_format}', f'--to={to_format}'],
            input=content,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({
                "error": "Pandoc conversion failed",
                "details": result.stderr
            }), 400
        
        return jsonify({
            "success": True,
            "output": result.stdout
        }), 200
    
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Conversion timeout"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/formats', methods=['GET'])
def get_formats():
    try:
        result_from = subprocess.run(
            ['pandoc', '--list-input-formats'],
            capture_output=True,
            text=True
        )
        
        result_to = subprocess.run(
            ['pandoc', '--list-output-formats'],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            "input_formats": result_from.stdout.strip().split('\n'),
            "output_formats": result_to.stdout.strip().split('\n')
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
